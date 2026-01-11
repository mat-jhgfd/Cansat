//! src/graph/data.rs
//!
//! Sliding-window live points, owned vector snapshots for widget lifetimes,
//! and bounded history storage.

use std::collections::VecDeque;

use super::config::GraphConfig;

#[derive(Debug)]
pub struct GraphData {
    /// points in the current visible sliding window (oldest at front)
    pub points: VecDeque<(f64, f64)>,

    /// an owned Vec copy of `points` kept around so we can hand a &'_ [(f64,f64)]
    /// slice to widgets that require a static-ish lifetime.
    pub data_vec: Vec<(f64, f64)>,

    /// full bounded history (kept bounded to ensure memory stays small)
    pub history: VecDeque<(f64, f64)>,

    /// config controlling window sizes and fallback ranges
    pub config: GraphConfig,
}

impl GraphData {
    /// Create a new GraphData with the provided config.
    pub fn new(config: GraphConfig) -> Self {
        let mid = (config.y_range.0 + config.y_range.1) / 2.0;
        // pre-fill sliding window with points at the midpoint
        let points: VecDeque<_> = (0..config.data_window).map(|x| (x as f64, mid)).collect();
        let data_vec = points.iter().copied().collect();
        let history = points.clone();
        Self {
            points,
            data_vec,
            history,
            config,
        }
    }

    /// Push a new point into the sliding window and bounded history.
    ///
    /// Maintains invariant: points.len() <= config.data_window, history.len() <= config.max_history.
    pub fn push_point(&mut self, x: f64, y: f64) {
        if self.points.len() == self.config.data_window {
            // drop oldest visible point
            self.points.pop_front();
        }
        self.points.push_back((x, y));

        // keep an owned vector for chart lifetimes
        self.data_vec.clear();
        self.data_vec.extend(self.points.iter().copied());

        // append to history and bound it
        self.history.push_back((x, y));
        while self.history.len() > self.config.max_history {
            self.history.pop_front();
        }
    }

    /// x bounds of the current sliding window (first, last)
    pub fn x_bounds(&self) -> (f64, f64) {
        let first = self.points.front().map(|p| p.0).unwrap_or(0.0);
        let last = self
            .points
            .back()
            .map(|p| p.0)
            .unwrap_or(first + self.points.len() as f64);
        (first, last)
    }

    /// (min, max, last) computed over the visible data_vec.
    ///
    /// Returns fallback values from config when data absent/non-finite.
    pub fn stats(&self) -> (f64, f64, f64) {
        let mut mn = f64::INFINITY;
        let mut mx = f64::NEG_INFINITY;
        for &(_, y) in &self.data_vec {
            if y < mn {
                mn = y;
            }
            if y > mx {
                mx = y;
            }
        }
        if mn == f64::INFINITY || mx == f64::NEG_INFINITY {
            // fallback to config range center if no valid data
            let (lo, hi) = self.config.y_range;
            let mid = (lo + hi) / 2.0;
            return (lo, hi, mid);
        }
        let last = self.data_vec.last().map(|(_, y)| *y).unwrap_or(0.0);
        (mn, mx, last)
    }
}
