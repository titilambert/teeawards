set expandtab           " enter spaces when tab is pressed
set textwidth=120       " break lines when line length increases
set tabstop=4           " use 4 spaces to represent tab
set softtabstop=4
set shiftwidth=4        " number of spaces to use for auto indent
set autoindent          " copy indent from current line when starting a new line

" make backspaces more powerfull
set backspace=indent,eol,start

set showcmd
syntax on                       " syntax highlighting
set paste
" Must be after set paste
set ruler                           " show line and column number

"set mouse=n

colorscheme elflord
set complete-=k complete+=k



if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif
endif


" Python
"highlight OverLength ctermbg=red ctermfg=white guibg=#592929
"match OverLength /\%80v.*/


set laststatus=2
hi User1 ctermfg=White ctermbg=Black
set statusline=%1*%-3.3n\ %f%(\ %r%)%(\ %#WarningMsg#%m%0*%)%1*%=%B\ (%l/%L,\ %c)\ %P\ [%{&encoding}:%{&fileformat}]%(\ %w%)\ %y\

"#call pathogen#infect()

let g:syntastic_python_checkers = ['python']
