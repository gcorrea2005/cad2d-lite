; grid.lsp — Parametric grid of beams/columns
; Usage: LSPLOAD examples/grid.lsp
; Draws a cols x rows grid with spacing-x, spacing-y

(defun grid (cols rows spacing-x spacing-y)
  (setq cx 0.0)
  (repeat* cols
    (lambda ()
      (line (p cx 0.0) (p cx (* rows spacing-y)))
      (setq cx (+ cx spacing-x))))
  (setq cy 0.0)
  (repeat* rows
    (lambda ()
      (line (p 0.0 cy) (p (* cols spacing-x) cy))
      (setq cy (+ cy spacing-y)))))

; Example: 5 columns, 3 rows, 100mm spacing X, 80mm spacing Y
(grid 5 3 100 80)
