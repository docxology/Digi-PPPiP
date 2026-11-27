# LaTeX Preamble

This file contains LaTeX packages and commands injected into the document
compilation process by `infrastructure/rendering/latex_utils.py`.

```latex
% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}

% Document layout
\usepackage[margin=0.65in]{geometry}
\usepackage{float}
\usepackage{graphicx}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}

% Code listings
\usepackage{listings}

% Typography and formatting
\usepackage{microtype}
\usepackage{xcolor}

% Cross-references and citations
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=red,
    urlcolor=red,
    citecolor=red,
    anchorcolor=red,
    filecolor=red
}
\usepackage[capitalise,noabbrev]{cleveref}
\usepackage{natbib}
```
