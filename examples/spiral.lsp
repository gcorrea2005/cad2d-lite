; spiral.lsp — Archimedean spiral as point cloud
; Usage: LSPLOAD examples/spiral.lsp

(defun spiral (cx cy turns segments max-radius)
  (setq a 0.0)
  (setq step (/ (* turns 6.28318) segments))
  (setq dr (/ max-radius segments))
  (setq r 0.0)
  (repeat* segments
    (lambda ()
      (setq x (+ cx (* r (cos a))))
      (setq y (+ cy (* r (sin a))))
      (point (p x y))
      (setq a (+ a step))
      (setq r (+ r dr)))))

; 3 turns, 200 points, 100mm max radius, centered at 200,200
(spiral 200 200 3 200 100)
