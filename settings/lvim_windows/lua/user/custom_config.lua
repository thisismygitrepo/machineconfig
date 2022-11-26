
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
require('dap-python').setup('~/ve/Scripts/ipython.exe')
