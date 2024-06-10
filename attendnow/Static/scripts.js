// Function to show notification
function showNotification(message) {
    var notification = document.getElementById('notification');
    var notificationMessage = document.getElementById('notification-message');
    notificationMessage.innerText = message;
    notification.style.display = 'block';
    setTimeout(function() {
        notification.style.display = 'none';
    }, 3000);
}
