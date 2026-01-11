//! src/main.rs
//!
//! Entrypoint delegating to `app::run()`.

mod app;
mod graph;
mod net;
mod panels;
mod ui;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    app::run()
}
