//! src/graph/shared.rs
//!
//! Shared per-graph state: view-state (autoscale/hysteresis), locking, and metadata.

use std::sync::{Arc, RwLock};

use super::config::GraphConfig;
use super::data::GraphData;
use ratatui::style::Color;

/// Stabilization state for view hysteresis.
#[derive(Clone, Copy, Debug)]
pub enum StabilizationState {
    Stable,
    Expanding,
    Shrinking,
}

/// View-related state mutated by the UI to implement autoscale/hysteresis.
#[derive(Debug)]
pub struct GraphViewState {
    /// Currently shown y-bounds (min, max). `None` means uninitialized.
    pub current_bounds: Option<(f64, f64)>,

    /// Consecutive frames considered 'comfortable' (used to confirm shrinking).
    pub stable_count: usize,

    /// Current stabilization phase.
    pub state: StabilizationState,
}

impl GraphViewState {
    /// Create a fresh view state.
    pub fn new() -> Self {
        Self {
            current_bounds: None,
            stable_count: 0,
            state: StabilizationState::Stable,
        }
    }
}

/// The authoritative shared graph object used across threads.
pub struct GraphShared {
    pub data: GraphData,
    pub view: GraphViewState,
    pub name: String,
    pub color: Color,
    pub autoscale: bool,
    pub smoothing: f64,
    pub locked_bounds: Option<(f64, f64)>,
    pub shrink_confirm_frames: usize,
    pub shrink_margin_frac: f64,
}

impl GraphShared {
    /// Construct `GraphShared`.
    pub fn new(
        cfg: GraphConfig,
        name: &str,
        color: Color,
        autoscale: bool,
        smoothing: f64,
    ) -> Self {
        Self {
            data: GraphData::new(cfg.clone()),
            view: GraphViewState::new(),
            name: name.to_string(),
            color,
            autoscale,
            smoothing: smoothing.clamp(0.0, 1.0),
            locked_bounds: None,
            shrink_confirm_frames: 8,
            shrink_margin_frac: 0.20,
        }
    }
}

/// Alias: Arc<RwLock<GraphShared>>
pub type SharedGraph = Arc<RwLock<GraphShared>>;

/// Alias for a write guard.
pub type GraphGuard<'a> = std::sync::RwLockWriteGuard<'a, GraphShared>;
