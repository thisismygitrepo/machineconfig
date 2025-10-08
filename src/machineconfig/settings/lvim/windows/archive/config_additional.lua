

lvim.colorscheme = "torte"

-- Additional Plugins
lvim.plugins = {
  -- {
  -- "folke/trouble.nvim",
  -- cmd = "TroubleToggle",
  -- },
  "mfussenegger/nvim-dap-python",
--   "akinsho/toggleterm.nvim",
  "stevearc/overseer.nvim",
}

require('overseer').setup()


require('dap').configurations.python = { {
  type = 'python',
  request = 'launch',
  args = { "-i" },
  name = 'My custom launch configuration',
  program = '${file}',
  pythonPath = function()
    return "${env:VIRTUAL_ENV}/Scripts/python.exe"
  end;
  -- ... more options, see https://github.com/microsoft/debugpy/wiki/Debug-configuration-settings
},
}


local dap = require('dap')
