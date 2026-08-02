'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2, Eye, EyeOff } from 'lucide-react'
import { useLogin } from '@/lib/queries'
import { isAuthenticated } from '@/lib/auth'
import { ApiError } from '@/lib/api'

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Enter a valid email'),
  password: z.string().min(1, 'Password is required'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const login = useLogin()

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  // Already signed in — skip the login screen.
  useEffect(() => {
    if (isAuthenticated()) router.replace('/dashboard')
  }, [router])

  const loading = isSubmitting || login.isPending

  async function onSubmit({ email, password }: LoginForm) {
    try {
      await login.mutateAsync({ email: email.trim(), password })
      router.replace('/dashboard')
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.status === 401
            ? 'Invalid email or password'
            : err.message
          : 'Unable to sign in. Please try again.'
      setError('root.serverError', { message })
    }
  }

  const serverError = errors.root?.serverError?.message

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-background px-4">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_oklch(0.28_0.04_250)_0%,_transparent_55%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.04] [background-image:linear-gradient(to_right,#fff_1px,transparent_1px),linear-gradient(to_bottom,#fff_1px,transparent_1px)] [background-size:48px_48px]"
      />

      <div className="relative w-full max-w-sm space-y-8">
        <div className="space-y-3 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <span className="text-sm font-bold tracking-tight">LF</span>
          </div>
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">LeadFlow</h1>
            <p className="text-sm text-muted-foreground">Sign in to the RevOps supervisor dashboard</p>
          </div>
        </div>

        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="space-y-4 rounded-xl border border-border bg-card/80 p-6 shadow-sm backdrop-blur-sm"
        >
          <div className="space-y-2">
            <label
              htmlFor="email"
              className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              autoComplete="username"
              aria-invalid={!!errors.email}
              disabled={loading}
              className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1 aria-[invalid=true]:border-destructive"
              {...register('email')}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="text-xs font-medium uppercase tracking-wide text-muted-foreground"
            >
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                placeholder="Enter admin password"
                aria-invalid={!!errors.password}
                disabled={loading}
                className="w-full rounded-lg border border-border bg-background px-3 py-2.5 pr-10 text-sm text-foreground outline-none ring-ring placeholder:text-muted-foreground focus:ring-1 aria-[invalid=true]:border-destructive"
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                tabIndex={-1}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>

          {serverError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
              {serverError}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-primary text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground">
          Sign in with the admin credentials from your backend <code className="text-foreground/80">.env</code>
        </p>
      </div>
    </div>
  )
}
