//! src/panels/title.rs
//!
//! Simple title/header panel.

use ratatui::{
    Frame,
    layout::Rect,
    widgets::{Block, Borders, Paragraph},
};

pub struct TitlePanel {
    pub title: String,
}

impl TitlePanel {
    pub fn new(title: &str) -> Self {
        Self {
            title: title.to_string(),
        }
    }
}

impl crate::ui::Panel for TitlePanel {
    fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        let p = Paragraph::new(self.title.clone())
            .block(Block::default().title("Title").borders(Borders::ALL));
        f.render_widget(p, area);
    }
}
