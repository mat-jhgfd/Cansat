//! src/graph.rs
//!
//! Top-level `graph` module exposing configuration and data types.

pub mod config;
pub mod data;
pub mod shared;

/// Re-exports
pub use config::GraphConfig;
pub use data::GraphData;
