//! src/panels/paragraph.rs
//!
//! Simple paragraph panel used for static help/text blocks.

use ratatui::{
    Frame,
    layout::Rect,
    widgets::{Block, Borders, Paragraph, Wrap},
};

/// Small reusable paragraph panel.
pub struct ParagraphPanel {
    pub text: String,
    pub title: String,
}

impl ParagraphPanel {
    pub fn new(text: &str, title: &str) -> Self {
        Self {
            text: text.to_string(),
            title: title.to_string(),
        }
    }
}

impl crate::ui::Panel for ParagraphPanel {
    fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        let p = Paragraph::new(self.text.clone())
            .wrap(Wrap { trim: true })
            .block(
                Block::default()
                    .title(self.title.clone())
                    .borders(Borders::ALL),
            );
        f.render_widget(p, area);
    }
}
