// SPDX-FileCopyrightText: 2026 The meson-python developers
//
// SPDX-License-Identifier: MIT

use pyo3::prelude::*;

#[pymodule]
mod rust_pyo3 {
    use pyo3::prelude::*;

    /// Sum two numbers.
    #[pyfunction]
    fn sum(a: i64, b: i64) -> PyResult<i64> {
        Ok(a + b)
    }
}
