//! src/panels/info.rs
//!
//! Graph info panel: shows current stabilization state, bounds, and toggles.

use ratatui::{
    Frame,
    layout::Rect,
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

use crate::graph::shared::SharedGraph;

/// Read-only info panel; `highlighted` affects border style.
pub struct InfoPanel {
    pub shared: SharedGraph,
    pub highlighted: bool,
}

impl InfoPanel {
    pub fn new(shared: SharedGraph) -> Self {
        Self {
            shared,
            highlighted: false,
        }
    }
}

impl crate::ui::Panel for InfoPanel {
    fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        let g = self.shared.read().unwrap();

        let state = match g.view.state {
            crate::graph::shared::StabilizationState::Stable => "Stable",
            crate::graph::shared::StabilizationState::Expanding => "Expanding",
            crate::graph::shared::StabilizationState::Shrinking => "Shrinking",
        };

        let bounds = g.view.current_bounds.unwrap_or(g.data.config.y_range);
        let lock_text = if g.locked_bounds.is_some() {
            " (locked)"
        } else {
            ""
        };

        let lines = vec![
            Line::from(vec![
                Span::styled(&g.name, Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(format!(
                    "{}  autoscale={}  smoothing={:.2}",
                    lock_text, g.autoscale, g.smoothing
                )),
            ]),
            Line::from(vec![Span::raw(format!(
                "state={}  bounds=[{:.3},{:.3}]",
                state, bounds.0, bounds.1
            ))]),
        ];

        let mut block = Block::default().title("Info").borders(Borders::ALL);
        if self.highlighted {
            block = block.style(
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD),
            );
        }

        f.render_widget(Paragraph::new(lines).block(block), area);
    }
}
