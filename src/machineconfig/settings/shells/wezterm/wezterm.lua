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

-- config.animation_fps = 60


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

--   -- Increase opacity
-- {
--   key = 'UpArrow',
--   mods = 'CTRL|SHIFT',
--   action = wezterm.action{AdjustWindowOpacity={delta=0.1}},
-- },

-- -- Decrease opacity
-- {
--   key = 'DownArrow',
--   mods = 'CTRL|SHIFT',
--   action = wezterm.action{AdjustWindowOpacity={delta=-0.1}},
-- }

  -- {
  --   key = '[',
  --   mods = 'CTRL|SHIFT',
  --   action = wezterm.action_callback(function(window, pane)
  --       adjust_opacity(window, -0.1)
  --   end),
  -- },
  -- {
  --   key = ']',
  --   mods = 'CTRL|SHIFT',
  --   action = wezterm.action_callback(function(window, pane)
  --       adjust_opacity(window, 0.1)
  --   end),
  -- },

}


-- config.color_scheme = 'shades-of-purple'
-- 'Pro' == 'Spiderman'  -- 'shades-of-purple'  -- 'synthwave' -- 'Symfonic'  -- 'PaulMillr'  -- 'Neon'  -- 'LiquidCarbonTransparentInverse' -- 'Laser'  -- 'IR_Black' -- 'Hurtado' -- 'Homebrew' -- Hipster Green'  -- Firefly Traditional' -- 'Elementary'  -- 'deep' -- 'Dark Pastel' -- 'Bright Lights' -- 'Adventure'  -- 'Nancy (terminal.sexy)'

config.colors = {
  -- Make the selection text color fully transparent.
  -- When fully transparent, the current text color will be used.
  -- selection_fg = 'none',
  -- Set the selection background color with alpha.
  -- When selection_bg is transparent, it will be alpha blended over
  -- the current cell background color, rather than replace it
  -- selection_bg = 'rgba(50% 50% 50% 50%)',
}

-- config.window_background_image = '/home/alex/Downloads/uni.jpg'
-- config.window_background_image_hsb = {
--   -- Darken the background image by reducing it to 1/3rd
--   brightness = 0.04,

--   -- You can adjust the hue by scaling its value.
--   -- a multiplier of 1.0 leaves the value unchanged.
--   hue = 1.0,

--   -- You can adjust the saturation also.
--   saturation = 0.5,
-- }


-- config.show_pane_ids = true
config.pane_focus_follows_mouse = true
config.inactive_pane_hsb = {
    saturation = 0.6,
    brightness = 0.6,
  }

-- config.ime_preedit_rendering = 'System'
config.enable_tab_bar = false
config.window_background_opacity = 0.98
config.text_background_opacity = 1.0
config.enable_scroll_bar = true
config.cursor_blink_rate = 1000
config.cursor_blink_ease_in = "Constant"
config.cursor_blink_ease_out = "Constant"

-- config.unicode_version = 7
-- c.force_reverse_video_cursor = true
-- config.font = 'JetBrains Mono'
-- config.font = wezterm.font 'Fira Code'
-- config.font = wezterm.font('Iosevka Term', { weight = 'Bold', italic = true,
--                                                experimental_bidi = true })
config.bidi_enabled = true

-- from https://wezfurlong.org/wezterm/config/launch.html#the-launcher-menu
if wezterm.target_triple == 'x86_64-pc-windows-msvc' then
  config.default_prog = { 'pwsh', '-NoLogo' }
end


-- see https://wezfurlong.org/wezterm/config/lua/window/set_config_overrides.html
local function adjust_opacity(window, delta)
  local overrides = window:get_config_overrides() or {}
  local current_opacity = overrides.window_background_opacity or 1.0
  local new_opacity = math.max(0.1, math.min(1.0, current_opacity + delta))
  overrides.window_background_opacity = new_opacity
  window:set_config_overrides(overrides)
end


-- and finally, return the configuration to wezterm
-- config.enable_osc133 = false  -- to silence: P>|WezTerm 20240203-110809-5046fc22\

return config
