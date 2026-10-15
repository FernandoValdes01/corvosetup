source /usr/share/cachyos-fish-config/cachyos-config.fish

# Disable CachyOS's Fastfetch welcome message.
function fish_greeting
end

# User tools
fish_add_path "$HOME/.local/bin"
fish_add_path "$HOME/.opencode/bin"
fish_add_path "$HOME/.mimocode/bin"

# Fastfetch shortcut
alias ff fastfetch
