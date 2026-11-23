const NAME_REGEX = /^[A-Za-zČĆŽŠĐčćžšđ' -]{2,50}$/
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

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

  const email = form.email.trim()
  if (!email) {
    errors.email = 'Imejl je obavezan.'
  } else if (email.length > 254 || !EMAIL_REGEX.test(email)) {
    errors.email = 'Imejl nije u ispravnom formatu.'
  }

  const password = form.password
  if (!password) {
    errors.password = 'Lozinka je obavezna.'
  } else if (password.length < 8 || password.length > 64) {
    errors.password = 'Lozinka mora imati između 8 i 64 karaktera.'
  } else if (
    !/[A-Z]/.test(password) ||
    !/[a-z]/.test(password) ||
    !/[0-9]/.test(password) ||
    !/[^A-Za-z0-9]/.test(password)
  ) {
    errors.password = 'Lozinka mora sadržati veliko slovo, malo slovo, cifru i specijalni karakter.'
  }

  if (form.confirmPassword !== password) {
    errors.confirmPassword = 'Lozinke se ne poklapaju.'
  }

  return errors
}