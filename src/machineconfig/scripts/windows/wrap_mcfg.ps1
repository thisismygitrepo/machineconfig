function wrap_in_shell_script {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    
    # Generate a random name (based on current timestamp hashed with SHA256)
    # Compute SHA256 of the timestamp string (don't pipe the string to Get-FileHash
    # because that attempts to treat the input as a path). Take the first 16 hex
    # chars as the random name.
    $ts = Get-Date -Format o
    try {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($ts)
        $hashBytes = $sha.ComputeHash($bytes)
        $hash = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()
        $randomName = $hash.Substring(0, 16)
    } finally {
        if ($sha) { $sha.Dispose() }
    }

    # Define the output path
    $env:OP_PROGRAM_PATH = "$HOME/tmp_results/tmp_scripts/machineconfig/${randomName}.ps1"

    # Run the specified command with its arguments
    & $Command @Arguments

    # Check if the file exists
    if (Test-Path $env:OP_PROGRAM_PATH) {
        Write-Host "🚀 Taking over from python script @ $env:OP_PROGRAM_PATH"
        try {
            bat --style=full --theme=OneHalfDark --paging=never "$env:OP_PROGRAM_PATH"
        } catch {
            # Write-Host "⚠️ Warning: Failed to display script content with 'bat'. Proceeding to execute the script."
            Write-Host " "
        }
        & $env:OP_PROGRAM_PATH
        # Write-Host "✅ '$Command' execution completed."

    } else {
        # Write-Host "✅ '$Command' execution completed."
        Write-Host " "
    }

    # Clean up the temporary environment variable so it doesn't leak to other processes/sessions
    try {
        Remove-Item Env:\OP_PROGRAM_PATH -ErrorAction SilentlyContinue
    } catch {
        # best-effort cleanup; ignore any errors
    }

    # Also explicitly clear the variable in the current process
    $env:OP_PROGRAM_PATH = $null
}

# Call the function with any arguments passed to the script
if ($args.Count -gt 0) {
    wrap_in_shell_script @args
}

