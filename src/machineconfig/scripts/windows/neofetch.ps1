
(Invoke-WebRequest "https://raw.githubusercontent.com/kiedtl/winfetch/master/winfetch.ps1" -UseBasicParsing).Content.Remove(0,1) | Invoke-Expression
