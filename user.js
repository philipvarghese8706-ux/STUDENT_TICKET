//self typed below ...

const button= document.querySelector('.button')
const qr= document.querySelector('.qr')
const name= document.querySelector('.name')

//when you click the button the qr must be displayed and the button must disappear..
button.onclick = () => {
    qr.style.display ='flex'
    button.style.display ='none'
}

function simulateScan(ticketCode) {
  fetch('http://localhost:5000/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code: ticketCode })
  })
  .then(response => response.json())
  .then(data => {
    if (data.valid) {
      qrBox.style.backgroundColor = '#4ade80'
      qrBox.textContent = '✓ Welcome, ' + data.name
    } else {
      qrBox.style.backgroundColor = '#f87171'
      qrBox.textContent = '✗ ' + data.message
    }
  })
}