const NAME_REGEX = /^[A-Za-zČĆŽŠĐčćžšđ' -]{2,50}$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const OTP_REGEX = /^[0-9]{6}$/

function getEmailError(value) {
  const email = value.trim()
  if (!email) {
    return 'Imejl je obavezan.'
  }
  if (email.length > 254 || !EMAIL_REGEX.test(email)) {
    return 'Imejl nije u ispravnom formatu.'
  }
  return ''
}

function getPasswordStrengthError(password) {
  if (!password) {
    return 'Lozinka je obavezna.'
  }
  if (password.length < 8 || password.length > 64) {
    return 'Lozinka mora imati između 8 i 64 karaktera.'
  }
  if (
    !/[A-Z]/.test(password) ||
    !/[a-z]/.test(password) ||
    !/[0-9]/.test(password) ||
    !/[^A-Za-z0-9]/.test(password)
  ) {
    return 'Lozinka mora sadržati veliko slovo, malo slovo, cifru i specijalni karakter.'
  }
  return ''
}

export function validateRegisterForm(form) {
  const errors = {}

  const firstName = form.firstName.trim()
  if (!firstName) {
    errors.firstName = 'Ime je obavezno.'
  } else if (!NAME_REGEX.test(firstName)) {
    errors.firstName = 'Ime može sadržati samo slova (2–50 karaktera).'
  }

  const lastName = form.lastName.trim()
  if (!lastName) {
    errors.lastName = 'Prezime je obavezno.'
  } else if (!NAME_REGEX.test(lastName)) {
    errors.lastName = 'Prezime može sadržati samo slova (2–50 karaktera).'
  }

  const emailError = getEmailError(form.email)
  if (emailError) {
    errors.email = emailError
  }

  const passwordError = getPasswordStrengthError(form.password)
  if (passwordError) {
    errors.password = passwordError
  }

  if (form.confirmPassword !== form.password) {
    errors.confirmPassword = 'Lozinke se ne poklapaju.'
  }

  return errors
}

export function validateLoginForm(form) {
  const errors = {}

  const emailError = getEmailError(form.email)
  if (emailError) {
    errors.email = emailError
  }

  if (!form.password) {
    errors.password = 'Lozinka je obavezna.'
  } else if (form.password.length > 64) {
    errors.password = 'Lozinka je predugačka.'
  }

  return errors
}

export function validateOtp(otp) {
  if (!otp) {
    return 'Kod je obavezan.'
  }
  if (!OTP_REGEX.test(otp)) {
    return 'Kod mora imati tačno 6 cifara.'
  }
  return ''
}

export function validateChangePasswordForm(form) {
  const errors = {}

  if (!form.currentPassword) {
    errors.currentPassword = 'Trenutna lozinka je obavezna.'
  } else if (form.currentPassword.length > 64) {
    errors.currentPassword = 'Lozinka je predugačka.'
  }

  const newPasswordError = getPasswordStrengthError(form.newPassword)
  if (newPasswordError) {
    errors.newPassword = newPasswordError
  } else if (form.newPassword === form.currentPassword) {
    errors.newPassword = 'Nova lozinka mora biti različita od trenutne.'
  }

  if (form.confirmNewPassword !== form.newPassword) {
    errors.confirmNewPassword = 'Lozinke se ne poklapaju.'
  }

  return errors
}

export function validateForgotPasswordForm(form) {
  const errors = {}

  const emailError = getEmailError(form.email)
  if (emailError) {
    errors.email = emailError
  }

  return errors
}

export function validateResetPasswordForm(form) {
  const errors = {}

  const newPasswordError = getPasswordStrengthError(form.newPassword)
  if (newPasswordError) {
    errors.newPassword = newPasswordError
  }

  if (form.confirmNewPassword !== form.newPassword) {
    errors.confirmNewPassword = 'Lozinke se ne poklapaju.'
  }

  return errors
}