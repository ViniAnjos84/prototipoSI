document.addEventListener("DOMContentLoaded", () => {

  const toastElement = document.getElementById("toastMsg");

  if (toastElement) {

    const toast = new bootstrap.Toast(toastElement, {
      delay: 3000
    });

    toast.show();
  }

});