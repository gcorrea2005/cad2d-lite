; bolt_holes.lsp — Circular bolt pattern
; Usage: LSPLOAD examples/bolt_holes.lsp

(defun bolt-circle (cx cy pitch-radius hole-count hole-radius)
  (setq angle-step (/ 360.0 hole-count))
  (setq i 0)
  (repeat* hole-count
    (lambda ()
      (setq ang (* i angle-step))
      (setq ang-rad (/ (* ang 3.14159) 180))
      (setq x (+ cx (* pitch-radius (cos ang-rad))))
      (setq y (+ cy (* pitch-radius (sin ang-rad))))
      (circle (p x y) hole-radius)
      (setq i (+ i 1)))))

; 8 bolts, 50mm pitch circle, 5mm holes, centered at 150,150
(bolt-circle 150 150 50 8 5)
