import { useState } from 'react'

export const useAuth = () => {
  const [user] = useState({
    name: 'Alex Thompson',
    email: 'alex@ecommerce.com',
    avatar: null,
    role: 'Admin'
  })

  return {
    user,
    isAuthenticated: true
  }
}