//! src/graph/config.rs
//!
//! Configuration values for graph behavior and memory bounding.
//!
//! Centralized parameters for window lengths, history size, and default ranges.

#[derive(Clone, Debug)]
pub struct GraphConfig {
    /// Number of data points visible in the live sliding window.
    pub data_window: usize,

    /// Maximum number of historical points to retain (bounded memory).
    pub max_history: usize,

    /// Default y-range to use when autoscale is disabled or as a fallback.
    pub y_range: (f64, f64),
}

impl GraphConfig {
    /// Create a new `GraphConfig`.
    pub fn new(data_window: usize, max_history: usize, y_range: (f64, f64)) -> Self {
        Self {
            data_window,
            max_history,
            y_range,
        }
    }
}

impl Default for GraphConfig {
    fn default() -> Self {
        Self {
            data_window: 60,
            max_history: 2_000,
            y_range: (-1.0, 1.0),
        }
    }
}
