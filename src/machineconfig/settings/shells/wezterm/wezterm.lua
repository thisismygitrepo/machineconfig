-- Pull in the wezterm API
local wezterm = require 'wezterm'
local mux = wezterm.mux

-- This table will hold the configuration.
local config = {}
act = wezterm.action
c = config

-- In newer versions of wezterm, use the config_builder which will
-- help provide clearer error messages
if wezterm.config_builder then
  config = wezterm.config_builder()
end

-- This is where you actually apply your config choices


wezterm.on('gui-attached', function(domain)
  -- maximize all displayed windows on startup
  local workspace = mux.get_active_workspace()
  for _, window in ipairs(mux.all_windows()) do
    if window:get_workspace() == workspace then
      window:gui_window():toggle_fullscreen()
    end
  end
end)

-- wezterm.on('gui-startup', function(cmd)
--   local tab, pane, window = mux.spawn_window(cmd or {})
--   window:gui_window():maximize()
-- end)


config.leader = { key = 'Space', mods = 'CTRL', timeout_milliseconds = 1000 }
config.keys = {
  {
    key = '+',
    mods = 'ALT|SHIFT',
    action = wezterm.action.SplitHorizontal { domain = 'CurrentPaneDomain' },
  },
  {
    key = '_',
    mods = 'ALT|SHIFT',
    action = wezterm.action.SplitVertical { domain = 'CurrentPaneDomain' },
  },
  {
    key = 'w',
    mods = 'CTRL|SHIFT',
    action = wezterm.action.CloseCurrentPane { confirm = false },
  },
  {
    key = '|',
    mods = 'CTRL|SHIFT',
    action = wezterm.action.RotatePanes 'CounterClockwise',
  },
  {
    key = 'Z',
    mods = 'CTRL',
    action = wezterm.action.TogglePaneZoomState,
  },
  {
    key = '0',
    mods = 'CTRL',
    action = wezterm.action.PaneSelect {
      mode = 'SwapWithActive',
    },
  },
  { key = '9', mods = 'CTRL', action = act.PaneSelect },


  { key = 'LeftArrow', mods = 'CTRL|SHIFT', action = act.AdjustPaneSize { 'Left', 1 } },
  -- { key = 'h', action = act.AdjustPaneSize { 'Left', 1 } },
  { key = 'RightArrow', mods = 'CTRL|SHIFT', action = act.AdjustPaneSize { 'Right', 1 } },
  -- { key = 'l', action = act.AdjustPaneSize { 'Right', 1 } },
  { key = 'UpArrow', mods = 'CTRL|SHIFT', action = act.AdjustPaneSize { 'Up', 1 } },
  -- { key = 'k', action = act.AdjustPaneSize { 'Up', 1 } },
  { key = 'DownArrow', mods = 'CTRL|SHIFT', action = act.AdjustPaneSize { 'Down', 1 } },
  -- { key = 'j', action = act.AdjustPaneSize { 'Down', 1 } },

  { key = 'LeftArrow', mods = 'ALT', action = act.ActivatePaneDirection 'Left' },
  -- { key = 'h', action = act.ActivatePaneDirection 'Left' },
  { key = 'RightArrow', mods = 'ALT', action = act.ActivatePaneDirection 'Right' },
  -- { key = 'l', action = act.ActivatePaneDirection 'Right' },
  { key = 'UpArrow', mods = 'ALT', action = act.ActivatePaneDirection 'Up' },
  -- { key = 'k', action = act.ActivatePaneDirection 'Up' },
  { key = 'DownArrow', mods = 'ALT', action = act.ActivatePaneDirection 'Down' },
  -- { key = 'j', action = act.ActivatePaneDirection 'Down' },

}



config.color_scheme = 'Builtin Dark'

-- config.window_background_image = '/path/to/wallpaper.jpg'
-- config.window_background_image_hsb = {
--   -- Darken the background image by reducing it to 1/3rd
--   brightness = 0.3,

--   -- You can adjust the hue by scaling its value.
--   -- a multiplier of 1.0 leaves the value unchanged.
--   hue = 1.0,

--   -- You can adjust the saturation also.
--   saturation = 1.0,
-- }


-- config.show_pane_ids = true
config.pane_focus_follows_mouse = true
config.inactive_pane_hsb = {
    saturation = 0.6,
    brightness = 0.6,
  }

-- config.ime_preedit_rendering = 'System'
config.enable_tab_bar = false
config.window_background_opacity = 1.0
config.text_background_opacity = 0.3
config.enable_scroll_bar = true
config.cursor_blink_rate = 1000
config.cursor_blink_ease_in = "Constant"
config.cursor_blink_ease_out = "Constant"
-- c.force_reverse_video_cursor = true

-- from https://wezfurlong.org/wezterm/config/launch.html#the-launcher-menu
if wezterm.target_triple == 'x86_64-pc-windows-msvc' then
  config.default_prog = { 'pwsh', '-NoLogo' }
end


-- and finally, return the configuration to wezterm
return config
