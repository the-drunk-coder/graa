;; Graa mode - (c)2015 by Niklas Reppel (nik@parkellipsen.de)

;; Drew heavy inspiration from Alex McLean's tidal-mode, and its
;; predecessors (even though this has not much to do with haskell ...)

(require 'scheme)
(require 'comint)
(require 'thingatpt)
(require 'find-lisp)
(require 'pulse)

(defvar graa-events
  '("triforce1"
   "circle"))

(defvar graa-keywords
      '("play" "expand" "add" "minus" "shift" "plus" "quit_graa" "stop" "pause"))

(defvar graa-font-lock-defaults
  `((
     ;; stuff between "
     ("\"\\.\\*\\?" . font-lock-string-face)
     ;; ; : , ; { } =>  @ $ = are all special elements
     ("-\\|:\\|,\\|<\\|>\\||\\|$\\|=" . font-lock-keyword-face)
     ( ,(regexp-opt graa-keywords 'words) . font-lock-builtin-face)
     ( ,(regexp-opt graa-events 'words) . font-lock-constant-face)
)))

(defvar graa-tab-width nil "Width of a tab for graa mode")

(defvar graa-buffer
  "*graa*"
  "*The name of the graa process buffer (default=*graa*).")

(defvar graa-interpreter
  "python"
  "*The graa interpeter to use .")

(defvar graa-interpreter-arguments
  (list ""
        )
  "*Arguments to the graa interpreter (default=none).")

(defun graa-buffer-filter (proc string)
  (unless (string-match "[:space:]graa>[:space:]" string) 
  (setq graa-output string))
  (when (buffer-live-p (process-buffer proc))
    (with-current-buffer (process-buffer proc)
      (let ((moving (= (point) (process-mark proc))))
	(save-excursion
	  ;; Insert the text, advancing the process marker.
	  (goto-char (process-mark proc))
	  (insert string)	  
	  (set-marker (process-mark proc) (point)))
	(if moving (goto-char (process-mark proc))))))
)

(defun graa-start ()
  "Start graa."
  (interactive)
  (if (comint-check-proc graa-buffer)
      (error "A graa process is already running")
    (apply
     'make-comint
     "graa"
     graa-interpreter
     nil)
    (graa-send-string "import sys")
    (graa-send-string "sys.path.append(\"/home/nik/REPOSITORIES/graa\")")    
    (graa-send-string "from graa import *")
    (graa-send-string "start_graa()")    
    (graa-see-output)
    (set-process-filter (get-buffer-process graa-buffer) 'graa-buffer-filter)
    )
  )

(defun graa-see-output ()
  "Show haskell output."
  (interactive)
  (when (comint-check-proc graa-buffer)
    (delete-other-windows)
    (split-window-horizontally)
    (with-current-buffer graa-buffer
      (let ((window (display-buffer (current-buffer))))
	(goto-char (point-max))
	(save-selected-window
	  (set-window-point window (point-max))
	  )
	)   
      )
    ;(select-window (get-buffer-window graa-buffer))
    ;(split-window-vertically)
    
   )
)

(defun graa-quit ()
  "Quit graa."
  (interactive)
  (kill-buffer graa-buffer)
  (delete-other-windows))

(defun chunk-string (n s)
  "Split a string into chunks of 'n' characters."
  (let* ((l (length s))
         (m (min l n))
         (c (substring s 0 m)))
    (if (<= l n)
        (list c)
      (cons c (chunk-string n (substring s n))))))

(defun graa-send-string (s)
  (if (comint-check-proc graa-buffer)
      (let ((cs (chunk-string 64 (concat s "\n"))))
        (mapcar (lambda (c) (comint-send-string graa-buffer c)) cs))
    (error "no graa process running?")))

(defun graa-run-line ()
  "Send the current line to the interpreter."
  (interactive)
  (let* ((s (buffer-substring (line-beginning-position)
			      (line-end-position)))
	 )
    (graa-send-string s))
  (pulse-momentary-highlight-one-line (point))
  (next-line)
  )

(defun graa-expand-line ()
  "Send the current line to the interpreter and insert result to current buffer"
  (interactive)
  (let* ((s (buffer-substring (line-beginning-position)
			      (line-end-position)))
	 )
    (graa-send-string s))
  (pulse-momentary-highlight-one-line (point))
  (next-line)
  (accept-process-output (get-buffer-process graa-buffer) 200)
  (newline)
  (insert "add(\"\"\"\n")
  (insert graa-output)
  (insert "\"\"\")")
)


(defun graa-run-multiple-lines ()
  "Send the current region to the interpreter as a single line."
  (interactive)
  (save-excursion
   (mark-paragraph)
   (let* ((s (buffer-substring-no-properties (region-beginning)
                                             (region-end)))
          )
     (graa-send-string s)     
     (mark-paragraph)
     (pulse-momentary-highlight-region (mark) (point))
     )
    )
  )


(defun graa-interrupt ()
  (interactive)
  (if (comint-check-proc graa-buffer)
      (with-current-buffer graa-buffer
	(interrupt-process (get-buffer-process (current-buffer))))
    (error "no graa process running?")))

(defvar graa-mode-map nil
  "graa keymap.")

(defun graa-mode-keybindings (map)
  "Graa keybindings."
  (define-key map [?\C-c ?\C-s] 'graa-start)
  (define-key map [?\C-c ?\C-v] 'graa-see-output)
  (define-key map [?\C-c ?\C-q] 'graa-quit)
  (define-key map [?\C-c ?\C-c] 'graa-run-line)
  (define-key map [?\C-c ?\C-x] 'graa-expand-line)
  (define-key map [?\C-c ?\C-a] 'graa-run-multiple-lines)
  (define-key map (kbd "<C-return>") 'graa-run-multiple-lines)
  (define-key map [?\C-c ?\C-i] 'graa-interrupt)
  )

(defun turn-on-graa-keybindings ()
  "Graa keybindings in the local map."
  (local-set-key [?\C-c ?\C-s] 'graa-start)
  (local-set-key [?\C-c ?\C-v] 'graa-see-output)
  (local-set-key [?\C-c ?\C-q] 'graa-quit)
  (local-set-key [?\C-c ?\C-c] 'graa-run-line)
  (local-set-key [?\C-c ?\C-a] 'graa-run-multiple-lines)
  (local-set-key (kbd "<C-return>") 'graa-run-multiple-lines)  
  (local-set-key [?\C-c ?\C-i] 'graa-interrupt)
  )

(defun graa-mode-menu (map)
  "Graa menu."
  (define-key map [menu-bar graa]
    (cons "Graa" (make-sparse-keymap "Graa")))
  (define-key map [menu-bar graa expression run-multiple-lines]
    '("Run multiple lines" . graa-run-multiple-lines))
  (define-key map [menu-bar graa expression run-line]
    '("Run line" . graa-run-line))
  (define-key map [menu-bar graa quit-graa]
    '("Quit graa" . graa-quit))
  (define-key map [menu-bar graa see-output]
    '("See output" . graa-see-output))
  (define-key map [menu-bar graa start]
    '("Start graa" . graa-start)))

(if graa-mode-map
    ()
  (let ((map (make-sparse-keymap "Graa")))
    (graa-mode-keybindings map)
    (graa-mode-menu map)
    (setq graa-mode-map map)))

(define-derived-mode
  graa-mode
  fundamental-mode
  "Graa"
  "Major mode for interacting with an inferior graa process."
  (electric-pair-mode)
  (setq font-lock-defaults graa-font-lock-defaults)
  ;(set (make-local-variable 'paragraph-start) "\f\\|[ \t]*$")
  ;(set (make-local-variable 'paragraph-separate) "[ \t\f]*$")					
  )

;; you again used quote when you had '((mydsl-hilite))
;; I just updated the variable to have the proper nesting (as noted above)
;; and use the value directly here
(setq font-lock-defaults graa-font-lock-defaults)

;; when there's an override, use it
;; otherwise it gets the default value
(when graa-tab-width
  (setq tab-width graa-tab-width))

;; for comments
;; overriding these vars gets you what (I think) you want
;; they're made buffer local when you set them
(setq comment-start "#")
(setq comment-end "")

(modify-syntax-entry ?# "< b" graa-mode-syntax-table)
(modify-syntax-entry ?\n "> b" graa-mode-syntax-table)

(add-to-list 'auto-mode-alist '("\\.graa$" . graa-mode))

(provide 'graa-mode)
