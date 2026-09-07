# Shell additions for the dev container, appended to the user's .bashrc during
# the image build.
#
# Two things live here: a prompt that shows the git branch and the active Python
# environment, and the selection of a default interpreter for work that is not
# managed by Poetry. The selection is stored in the container's own layer, so it
# survives a restart and is gone after a rebuild.

_dc_python_file="${HOME}/.config/devcontainer/python-version"
_dc_venv_root="${HOME}/.venvs"

# The activate script of a virtual environment edits PS1 on its own. Ours
# already shows the environment, so switch that off before anything activates.
export VIRTUAL_ENV_DISABLE_PROMPT=1

# --- prompt ------------------------------------------------------------------

_dc_git_branch() {
    local branch
    branch="$(git branch --show-current 2>/dev/null)" || return 0
    [ -n "$branch" ] && printf ' (%s)' "$branch"
}

_dc_env_name() {
    [ -n "$VIRTUAL_ENV" ] && printf ' [%s]' "${VIRTUAL_ENV##*/}"
}

PS1='\u@\h:\w$(_dc_git_branch)$(_dc_env_name)\$ '

# --- interpreter selection ---------------------------------------------------

_dc_activate() {
    [ -f "$1/bin/activate" ] || return 1
    # shellcheck source=/dev/null
    . "$1/bin/activate"
}

_dc_venv_path() {
    printf '%s/py%s' "$_dc_venv_root" "${1//./}"
}

# use-python                -> report the current selection and what is prepared
# use-python 3.11           -> fetch the interpreter if needed, prepare an
#                              environment, remember it, activate it now
# use-python system         -> drop the selection, back to the system interpreter
use-python() {
    local version="$1" venv

    if [ -z "$version" ]; then
        printf 'selected:  %s\n' "$(cat "$_dc_python_file" 2>/dev/null || printf 'system')"
        printf 'prepared:  %s\n' "$(ls -1 "$_dc_venv_root" 2>/dev/null | tr '\n' ' ')"
        return 0
    fi

    if [ "$version" = "system" ]; then
        rm -f "$_dc_python_file"
        command -v deactivate >/dev/null 2>&1 && deactivate
        printf 'using the system interpreter from now on\n'
        return 0
    fi

    venv="$(_dc_venv_path "$version")"
    if [ ! -d "$venv" ]; then
        printf 'preparing an environment for Python %s ...\n' "$version"
        uv venv --python "$version" --seed "$venv" || return 1
    fi

    mkdir -p "${_dc_python_file%/*}"
    printf '%s\n' "$version" > "$_dc_python_file"
    _dc_activate "$venv"
}

# Apply a stored selection when a new shell opens. Poetry activates its own
# environment later and wins; the prompt shows whichever one is in effect.
if [ -z "$VIRTUAL_ENV" ] && [ -r "$_dc_python_file" ]; then
    _dc_activate "$(_dc_venv_path "$(cat "$_dc_python_file")")" 2>/dev/null
fi
