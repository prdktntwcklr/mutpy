# enable color support of ls
alias ls='ls --color=auto'

# enable git autocompletion
if [ -f /usr/share/bash-completion/completions/git ]; then
    source /usr/share/bash-completion/completions/git
fi

# install pre-commit hooks
pip install pre-commit && pre-commit install
