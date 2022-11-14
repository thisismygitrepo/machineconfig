

lvim.colorscheme = "torte"

-- Additional Plugins
lvim.plugins = {
  -- {
  -- "folke/trouble.nvim",
  -- cmd = "TroubleToggle",
  -- },
  "mfussenegger/nvim-dap-python",
  "akinsho/toggleterm.nvim",
  "stevearc/overseer.nvim",
}

-- require('dap-python').setup('~/venvs/ve/Scripts/python.exe')
require('dap').configurations.python = { {
  type = 'python',
  request = 'launch',
  args = { "-i" },
  name = 'My custom launch configuration',
  program = '${file}',
  -- ... more options, see https://github.com/microsoft/debugpy/wiki/Debug-configuration-settings
}
}

require('overseer').setup()
