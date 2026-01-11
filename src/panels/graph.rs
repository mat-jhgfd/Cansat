//! src/panels/graph.rs
//!
//! Graph panel: renders the live chart, stats row, and optional locked-bounds lines.
//!
//! This panel keeps rendering-only logic here, computing target bounds, interpolating
//! view bounds with smoothing, and preparing datasets for the chart widget.

use ratatui::{
    Frame,
    layout::Rect,
    style::{Color, Modifier, Style},
    symbols,
    widgets::{Axis, Block, Borders, Chart, Dataset, Paragraph},
};

use crate::graph::shared::SharedGraph;

/// A lightweight wrapper around the shared graph state used for rendering.
pub struct GraphPanel {
    pub shared: SharedGraph,
}

impl GraphPanel {
    /// Create a new GraphPanel for a shared graph.
    pub fn new(shared: SharedGraph) -> Self {
        Self { shared }
    }

    /// Compute a target (ymin, ymax) for the current visible data (with padding).
    ///
    /// # Arguments
    /// * `data` - reference to `GraphData`.
    ///
    /// # Returns
    /// A `(min, max)` pair with padding applied. Falls back to `data.config.y_range`
    /// when data is absent or non-finite.
    fn compute_target_bounds(data: &crate::graph::GraphData) -> (f64, f64) {
        let slice = data.data_vec.as_slice();
        if slice.is_empty() {
            return data.config.y_range;
        }
        let mut mn = f64::INFINITY;
        let mut mx = f64::NEG_INFINITY;
        for &(_, y) in slice {
            if y < mn {
                mn = y;
            }
            if y > mx {
                mx = y;
            }
        }
        if !mn.is_finite() || !mx.is_finite() {
            return data.config.y_range;
        }
        if (mx - mn).abs() < f64::EPSILON {
            // data is essentially flat: add absolute padding to show a visible line
            let pad = (mn.abs().max(1.0)) * 0.1;
            (mn - pad, mx + pad)
        } else {
            // proportional padding (10% of range)
            let range = mx - mn;
            let pad = range * 0.1;
            (mn - pad, mx + pad)
        }
    }

    /// Interpolate from current bounds toward target by alpha in [0,1].
    ///
    /// # Arguments
    /// * `current` - current (min,max) bounds.
    /// * `target` - target (min,max) bounds.
    /// * `alpha` - interpolation factor; 0 => stay, 1 => snap to target.
    ///
    /// # Returns
    /// Interpolated bounds.
    fn interp_bounds(current: (f64, f64), target: (f64, f64), alpha: f64) -> (f64, f64) {
        let a = alpha.clamp(0.0, 1.0);
        let (cmin, cmax) = current;
        let (tmin, tmax) = target;
        (cmin * (1.0 - a) + tmin * a, cmax * (1.0 - a) + tmax * a)
    }
}

impl crate::ui::Panel for GraphPanel {
    /// Draw the graph panel into the provided frame and area.
    ///
    /// # Behavior
    /// * Renders a stats row with min/max/last values.
    /// * Computes target bounds (respecting locked bounds) and applies hysteresis:
    ///   - If data is out-of-bounds, expand toward target with smoothing.
    ///   - If data is comfortably inside current bounds for enough frames, shrink.
    ///   - If smoothing == 1.0, snap immediately when comfortable.
    fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        let chunks = ratatui::layout::Layout::default()
            .direction(ratatui::layout::Direction::Vertical)
            .constraints([
                ratatui::layout::Constraint::Length(3),
                ratatui::layout::Constraint::Min(0),
            ])
            .split(area);

        let mut g = self.shared.write().unwrap();

        // Stats row (min, max, last)
        let (mn, mx, last) = g.data.stats();
        // Compute global min/max from history
        let mut global_min = f64::INFINITY;
        let mut global_max = f64::NEG_INFINITY;
        for &(_, y) in &g.data.history {
            if y < global_min {
                global_min = y;
            }
            if y > global_max {
                global_max = y;
            }
        }
        // Display global min/max in the stats row
        let stats_text = format!(
            "Min: {:.3}  Max: {:.3}  Last: {:.3}",
            global_min, global_max, last
        );
        let stats_par =
            Paragraph::new(stats_text).block(Block::default().title("Stats").borders(Borders::ALL));
        f.render_widget(stats_par, chunks[0]);

        // determine target bounds (respect locked bounds first)
        let target_bounds = if let Some(bounds) = g.locked_bounds {
            bounds
        } else if g.autoscale {
            GraphPanel::compute_target_bounds(&g.data)
        } else {
            g.data.config.y_range
        };

        // initialize current bounds if needed
        if g.view.current_bounds.is_none() {
            g.view.current_bounds = Some(target_bounds);
            g.view.stable_count = 0;
            g.view.state = crate::graph::shared::StabilizationState::Stable;
        }

        let mut current = g.view.current_bounds.unwrap();

        if g.locked_bounds.is_some() {
            g.view.state = crate::graph::shared::StabilizationState::Stable;
        } else {
            let out_of_bounds = mn < current.0 || mx > current.1;
            if out_of_bounds {
                g.view.state = crate::graph::shared::StabilizationState::Expanding;
                g.view.stable_count = 0;
                let alpha = (g.smoothing.max(0.5)).clamp(0.0, 1.0);
                current = GraphPanel::interp_bounds(current, target_bounds, alpha);
                g.view.current_bounds = Some(current);
            } else {
                let (cmin, cmax) = current;
                let range = (cmax - cmin).abs().max(1e-9);
                let margin = g.shrink_margin_frac * range;
                let comfortable =
                    target_bounds.0 >= (cmin + margin) && target_bounds.1 <= (cmax - margin);
                if comfortable {
                    g.view.stable_count += 1;
                    if g.view.stable_count >= g.shrink_confirm_frames {
                        g.view.state = crate::graph::shared::StabilizationState::Shrinking;
                        current = GraphPanel::interp_bounds(current, target_bounds, g.smoothing);
                        g.view.current_bounds = Some(current);
                    } else {
                        g.view.state = crate::graph::shared::StabilizationState::Stable;
                    }
                } else {
                    g.view.stable_count = 0;
                    g.view.state = crate::graph::shared::StabilizationState::Stable;
                    if (g.smoothing - 1.0).abs() < f64::EPSILON {
                        current = GraphPanel::interp_bounds(current, target_bounds, 1.0);
                        g.view.current_bounds = Some(current);
                    }
                }
            }
        }

        // Keep dataset vectors alive until Chart::new() uses them
        let (ymin, ymax) = g.view.current_bounds.unwrap_or(g.data.config.y_range);
        let (xmin, xmax) = g.data.x_bounds();
        let series_owned = g.data.data_vec.clone();

        let mut datasets: Vec<Dataset> = Vec::new();
        datasets.push(
            Dataset::default()
                .name(g.name.clone())
                .marker(symbols::Marker::Braille)
                .graph_type(ratatui::widgets::GraphType::Line)
                .style(Style::default().fg(g.color))
                .data(series_owned.as_slice()),
        );

        let top_line = Some(vec![(xmin, ymax), (xmax, ymax)]);
        let bot_line = Some(vec![(xmin, ymin), (xmax, ymin)]);
        if g.locked_bounds.is_some() {
            if let Some(ref tl) = top_line {
                datasets.push(
                    Dataset::default()
                        .name("top")
                        .marker(symbols::Marker::Dot)
                        .graph_type(ratatui::widgets::GraphType::Line)
                        .style(Style::default().fg(Color::Red).add_modifier(Modifier::BOLD))
                        .data(tl.as_slice()),
                );
            }
            if let Some(ref bl) = bot_line {
                datasets.push(
                    Dataset::default()
                        .name("bot")
                        .marker(symbols::Marker::Dot)
                        .graph_type(ratatui::widgets::GraphType::Line)
                        .style(Style::default().fg(Color::Red).add_modifier(Modifier::BOLD))
                        .data(bl.as_slice()),
                );
            }
        }

        // y-axis labels
        let mut y_labels: Vec<String> = Vec::with_capacity(5);
        let span = (ymax - ymin).max(1e-9);
        for i in 0..5 {
            let v = ymin + span * (i as f64) / 4.0;
            y_labels.push(format!("{:.3}", v));
        }

        let chart = Chart::new(datasets)
            .block(Block::default().title(g.name.clone()).borders(Borders::ALL))
            .x_axis(Axis::default().bounds([xmin, xmax]))
            .y_axis(Axis::default().bounds([ymin, ymax]).labels(y_labels));

        f.render_widget(chart, chunks[1]);
    }
}
