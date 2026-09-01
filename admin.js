async function uploadCSV(){
    const fileInput=document.getElementById('csvFile')
    const UploadButton = document.getElementById('UploadButton')
    const progressBox = document.getElementById('progressBox')
    const log = document.getElementById('log')
    const summary = document.getElementById('summary')

    //we must put a message if a file is not selected.

    if(!fileInput.files[0]){
        alert('Please select a csv file')
        return
    }

    // We must disable button while processing
    UploadButton.disabled = true
    UploadButton.textContent = 'Processing...'

    // To show the progress box
    progressBox.classList.remove('hidden')
    log.innerHTML = ''
    summary.innerHTML = ''


    // Package the file for sending
    const formData = new FormData()
    formData.append('file', fileInput.files[0])

    addLog('Uploading CSV...', 'normal')


    try {
    const response = await fetch('/admin/upload', {
      method: 'POST',
      body: formData       // no Content-Type header — FormData sets it automatically
    })

    const data = await response.json()

    // Show each student's result in the log
    data.results.forEach(result => {
      if (result.success) {
        addLog(`✓ ${result.name} (${result.roll_number}) — ticket sent`, 'ok')
      } else {
        addLog(`✗ ${result.name} — ${result.error}`, 'error')
      }
    })

    // Show final summary
    summary.innerHTML = `
      Done. ${data.success_count} tickets sent,
      ${data.error_count} failed.
    `

    } catch (error) {
     addLog('Something went wrong — check the server', 'error')
    }

    // Re-enable button
    UploadButton.disabled = false
    UploadButton.textContent = 'Generate and Send Tickets'
}

function addLog(message, type) {
  const log = document.getElementById('log')
  const line = document.createElement('div')
  line.textContent = message
  line.className = type === 'ok' ? 'log-ok' :
                   type === 'error' ? 'log-err' : 'log-line'
  log.appendChild(line)
  log.scrollTop = log.scrollHeight   // auto-scroll to latest line
}

 



