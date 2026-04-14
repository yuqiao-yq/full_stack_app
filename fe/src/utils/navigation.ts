export function resolveRedirectPath(value: unknown) {
  if (typeof value !== 'string') {
    return '/'
  }

  if (!value.startsWith('/') || value.startsWith('//')) {
    return '/'
  }

  if (value === '/login' || value === '/register') {
    return '/'
  }

  return value
}

export function buildLoginRedirectPath() {
  const currentPath =
    window.location.pathname + window.location.search + window.location.hash

  if (currentPath.startsWith('/login') || currentPath.startsWith('/register')) {
    return '/login'
  }

  return `/login?redirect=${encodeURIComponent(currentPath)}`
}
