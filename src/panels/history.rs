//! src/panels/history.rs
//!
//! History panel: renders a scrolling, bounded history list for a graph.

use ratatui::{
    Frame,
    layout::Rect,
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Paragraph},
};

use crate::graph::shared::SharedGraph;

/// Shows the most recent entries of the shared graph's bounded history.
pub struct HistoryPanel {
    pub shared: SharedGraph,
}

impl HistoryPanel {
    /// Create a new HistoryPanel.
    pub fn new(shared: SharedGraph) -> Self {
        Self { shared }
    }
}

impl crate::ui::Panel for HistoryPanel {
    fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        let g = self.shared.read().unwrap();
        let height = area.height as usize;
        let hlen = g.data.history.len();
        let start = hlen.saturating_sub(height);
        let last_index = hlen.saturating_sub(1);

        // Collect references so we can index & style entries.
        let refs: Vec<&(f64, f64)> = g.data.history.iter().collect();

        let lines: Vec<Line> = refs
            .iter()
            .enumerate()
            .skip(start)
            .map(|(i, &&(x, y))| {
                let is_latest = i == last_index;
                let xs = if is_latest {
                    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
                } else {
                    Style::default().fg(Color::Green)
                };
                let ys = if is_latest {
                    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD)
                } else {
                    Style::default().fg(Color::Cyan)
                };
                Line::from(vec![
                    Span::styled("x: ", Style::default().fg(Color::Yellow)),
                    Span::styled(format!("{:>6.0}", x), xs),
                    Span::raw(", "),
                    Span::styled("y: ", Style::default().fg(Color::Yellow)),
                    Span::styled(format!("{:.3}", y), ys),
                ])
            })
            .collect();

        let block = Block::default().title("History").borders(Borders::ALL);
        f.render_widget(Paragraph::new(lines).block(block), area);
    }
}
