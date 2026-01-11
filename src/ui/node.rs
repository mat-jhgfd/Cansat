//! src/ui/node.rs
//!
//! Recursive layout Node + Panel trait used across the UI.

use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};

/// Panel trait: any renderable surface implements this.
pub trait Panel {
    fn draw(&self, f: &mut Frame<'_>, area: Rect);
}

/// Node tree used to compose the UI each frame.
pub enum Node {
    Group {
        direction: Direction,
        constraints: Vec<Constraint>,
        children: Vec<Node>,
    },
    Leaf {
        panel: Box<dyn Panel>,
    },
}

impl Node {
    /// Draw the node into the given area.
    pub fn draw(&self, f: &mut Frame<'_>, area: Rect) {
        match self {
            Node::Group {
                direction,
                constraints,
                children,
            } => {
                let chunks = Layout::default()
                    .direction(*direction)
                    .constraints(constraints.clone())
                    .split(area);
                for (child, chunk) in children.iter().zip(chunks.iter()) {
                    child.draw(f, *chunk);
                }
            }
            Node::Leaf { panel } => {
                panel.draw(f, area);
            }
        }
    }
}

/// Helper: create a group node.
pub fn group(direction: Direction, constraints: Vec<Constraint>, children: Vec<Node>) -> Node {
    Node::Group {
        direction,
        constraints,
        children,
    }
}

/// Helper: create a leaf node.
pub fn leaf(panel: Box<dyn Panel>) -> Node {
    Node::Leaf { panel }
}
