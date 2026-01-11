//! src/panels.rs
//!
//! Top-level panels module and re-exports.

pub mod graph;
pub mod history;
pub mod info;
pub mod paragraph;
pub mod title;

pub use graph::GraphPanel;
pub use history::HistoryPanel;
pub use info::InfoPanel;
pub use paragraph::ParagraphPanel;
pub use title::TitlePanel;
