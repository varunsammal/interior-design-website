document.addEventListener('DOMContentLoaded', function() {
    const profileImageInput = document.getElementById('profile_image');
    const currentProfilePic = document.getElementById('currentProfilePic');
    const newProfilePicPreview = document.getElementById('newProfilePicPreview');
    const defaultProfileIcon = document.getElementById('defaultProfileIcon');
    const changePictureBtn = document.getElementById('changePictureBtn');
    const removePictureBtn = document.getElementById('removePictureBtn');
    const removeProfileImageHiddenInput = document.getElementById('remove_profile_image');

    // Trigger file input when 'Change Picture' button is clicked
    changePictureBtn.addEventListener('click', function() {
        profileImageInput.click();
    });

    // Handle file selection for preview
    profileImageInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                newProfilePicPreview.src = e.target.result;
                newProfilePicPreview.classList.remove('d-none');
                newProfilePicPreview.classList.add('d-block');
                currentProfilePic.classList.remove('d-block');
                currentProfilePic.classList.add('d-none');
                defaultProfileIcon.classList.remove('d-block');
                defaultProfileIcon.classList.add('d-none');
                removePictureBtn.classList.remove('d-none');
                removePictureBtn.classList.add('d-block');
                removeProfileImageHiddenInput.value = '0'; // Ensure removal flag is off if new image is selected
            };
            reader.readAsDataURL(file);
        } else {
            // If no file is selected (e.g., user cancels file dialog)
            newProfilePicPreview.src = '';
            newProfilePicPreview.classList.remove('d-block');
            newProfilePicPreview.classList.add('d-none');

            // Revert to current or default based on if current profile pic exists
            if (currentProfilePic.src && !currentProfilePic.src.includes('default_profile.png')) {
                currentProfilePic.classList.remove('d-none');
                currentProfilePic.classList.add('d-block');
                defaultProfileIcon.classList.remove('d-block');
                defaultProfileIcon.classList.add('d-none');
                removePictureBtn.classList.remove('d-none');
                removePictureBtn.classList.add('d-block');
            } else {
                defaultProfileIcon.classList.remove('d-none');
                defaultProfileIcon.classList.add('d-block');
                currentProfilePic.classList.remove('d-block');
                currentProfilePic.classList.add('d-none');
                removePictureBtn.classList.remove('d-block');
                removePictureBtn.classList.add('d-none');
            }
        }
    });

    // Handle 'Remove Picture' button click
    removePictureBtn.addEventListener('click', function() {
        profileImageInput.value = ''; // Clear the file input
        newProfilePicPreview.src = '';
        newProfilePicPreview.classList.remove('d-block');
        newProfilePicPreview.classList.add('d-none');
        currentProfilePic.classList.remove('d-block');
        currentProfilePic.classList.add('d-none');
        defaultProfileIcon.classList.remove('d-none');
        defaultProfileIcon.classList.add('d-block');
        removePictureBtn.classList.remove('d-block');
        removePictureBtn.classList.add('d-none');
        removeProfileImageHiddenInput.value = '1'; // Set flag for backend to remove image
    });
}); 