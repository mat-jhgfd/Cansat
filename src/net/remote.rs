//! src/net/remote.rs
//!
//! Tiny line-based TCP control server for remote bindings.

use std::io::{BufRead, BufReader, Write};
use std::net::{Shutdown, TcpListener, TcpStream};
use std::sync::Arc;
use std::thread;

use crate::graph::shared::{GraphGuard, SharedGraph};

/// Start the remote TCP server and spawn a handler thread per client.
pub fn remote_server(addr: &str, graphs: Vec<SharedGraph>) {
    let graphs = Arc::new(graphs);
    let listener = match TcpListener::bind(addr) {
        Ok(l) => l,
        Err(e) => {
            eprintln!("remote_server: bind error {} on {}", e, addr);
            return;
        }
    };

    for stream in listener.incoming() {
        match stream {
            Ok(s) => {
                let g = graphs.clone();
                thread::spawn(move || handle_remote_client(s, g));
            }
            Err(e) => {
                eprintln!("remote_server: accept error: {}", e);
            }
        }
    }
}

/// Handle a single client; simple whitespace-split ASCII commands.
///
/// Commands:
/// - `toggle autoscale <idx>`
/// - `set smoothing <idx> <val>`
/// - `lock <idx>`
/// - `unlock <idx>`
/// - `quit`
pub fn handle_remote_client(mut s: TcpStream, graphs: Arc<Vec<SharedGraph>>) {
    let _peer = s
        .peer_addr()
        .map(|a| a.to_string())
        .unwrap_or_else(|_| "<peer?>".into());
    let mut rdr = BufReader::new(s.try_clone().unwrap());
    let mut line = String::new();

    loop {
        line.clear();
        if rdr.read_line(&mut line).is_err() {
            break;
        }
        if line.is_empty() {
            break;
        }
        let raw = line.trim();
        if raw.is_empty() {
            continue;
        }
        let parts: Vec<_> = raw.split_whitespace().collect();
        if parts.is_empty() {
            let _ = s.write_all(b"ERR empty\n");
            continue;
        }

        let mut reply = "OK\n".to_string();
        match parts[0].to_lowercase().as_str() {
            "toggle" if parts.len() == 3 && parts[1].eq_ignore_ascii_case("autoscale") => {
                if let Ok(idx) = parts[2].parse::<usize>() {
                    if let Some(gs) = graphs.get(idx) {
                        let mut g: GraphGuard<'_> = gs.write().unwrap();
                        g.autoscale = !g.autoscale;
                        if g.autoscale {
                            g.locked_bounds = None;
                        }
                    } else {
                        reply = format!("ERR no graph {}\n", idx);
                    }
                } else {
                    reply = "ERR idx\n".to_string();
                }
            }

            "set" if parts.len() == 4 && parts[1].eq_ignore_ascii_case("smoothing") => {
                if let Ok(idx) = parts[2].parse::<usize>() {
                    if let Ok(val) = parts[3].parse::<f64>() {
                        if let Some(gs) = graphs.get(idx) {
                            let mut g: GraphGuard<'_> = gs.write().unwrap();
                            g.smoothing = val.clamp(0.0, 1.0);
                        } else {
                            reply = format!("ERR no graph {}\n", idx);
                        }
                    } else {
                        reply = "ERR val\n".to_string();
                    }
                } else {
                    reply = "ERR idx\n".to_string();
                }
            }

            "lock" if parts.len() == 2 => {
                if let Ok(idx) = parts[1].parse::<usize>() {
                    if let Some(gs) = graphs.get(idx) {
                        let mut g: GraphGuard<'_> = gs.write().unwrap();
                        if let Some(cb) = g.view.current_bounds {
                            g.locked_bounds = Some(cb);
                        } else {
                            reply = "ERR no_bounds\n".to_string();
                        }
                    } else {
                        reply = format!("ERR no graph {}\n", idx);
                    }
                } else {
                    reply = "ERR idx\n".to_string();
                }
            }

            "unlock" if parts.len() == 2 => {
                if let Ok(idx) = parts[1].parse::<usize>() {
                    if let Some(gs) = graphs.get(idx) {
                        let mut g: GraphGuard<'_> = gs.write().unwrap();
                        g.locked_bounds = None;
                    } else {
                        reply = format!("ERR no graph {}\n", idx);
                    }
                } else {
                    reply = "ERR idx\n".to_string();
                }
            }

            "quit" => {
                reply = "OK bye\n".to_string();
                let _ = s.write_all(reply.as_bytes());
                break;
            }

            _ => {
                reply = format!("ERR unknown {}\n", parts.join(" "));
            }
        }
        let _ = s.write_all(reply.as_bytes());
    }

    let _ = s.shutdown(Shutdown::Both);
}
