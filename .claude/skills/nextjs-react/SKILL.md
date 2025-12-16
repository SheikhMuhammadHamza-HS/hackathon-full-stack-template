---
name: nextjs-react
description: Next.js 16+ and React 19 skill for building modern web applications. Use when working with Next.js App Router, Server Components, Client Components, Server Actions, routing, data fetching, or React 19 features like useActionState, useOptimistic, and use hook. Triggers on keywords like Next.js, React, App Router, Server Component, Client Component, Server Action, SSR, RSC.
---

# Next.js 16+ & React 19 Skill

## Overview

Next.js is a React framework for building full-stack web applications. Next.js 16+ uses the App Router with React Server Components by default, providing excellent performance and developer experience.

## Installation

```bash
# Create new Next.js app
npx create-next-app@latest my-app

# With TypeScript (recommended)
npx create-next-app@latest my-app --typescript

# Manual installation
npm install next@latest react@latest react-dom@latest
```

## Project Structure

```
my-app/
├── app/                    # App Router (recommended)
│   ├── layout.tsx          # Root layout (required)
│   ├── page.tsx            # Home page (/)
│   ├── globals.css         # Global styles
│   ├── about/
│   │   └── page.tsx        # /about
│   ├── blog/
│   │   ├── page.tsx        # /blog
│   │   └── [slug]/
│   │       └── page.tsx    # /blog/[slug]
│   └── api/
│       └── route.ts        # API route
├── components/             # Shared components
├── lib/                    # Utility functions
├── public/                 # Static files
├── next.config.js          # Next.js config
└── package.json
```

## File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Page component for route |
| `layout.tsx` | Shared layout wrapper |
| `loading.tsx` | Loading UI (Suspense fallback) |
| `error.tsx` | Error boundary |
| `not-found.tsx` | 404 page |
| `template.tsx` | Re-renders on navigation |
| `route.ts` | API endpoint |
| `default.tsx` | Parallel route fallback |

## Routing

### Basic Pages

```tsx
// app/page.tsx - Home page (/)
export default function Home() {
  return <h1>Welcome</h1>
}

// app/about/page.tsx - About page (/about)
export default function About() {
  return <h1>About Us</h1>
}

// app/blog/page.tsx - Blog list (/blog)
export default function Blog() {
  return <h1>Blog Posts</h1>
}
```

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx - Dynamic route (/blog/my-post)
export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  return <h1>Post: {slug}</h1>
}

// app/shop/[...categories]/page.tsx - Catch-all (/shop/a/b/c)
export default async function Category({
  params,
}: {
  params: Promise<{ categories: string[] }>
}) {
  const { categories } = await params
  return <h1>Categories: {categories.join('/')}</h1>
}
```

### Route Groups

```
app/
├── (marketing)/           # Group - doesn't affect URL
│   ├── about/page.tsx     # /about
│   └── contact/page.tsx   # /contact
├── (shop)/
│   ├── products/page.tsx  # /products
│   └── cart/page.tsx      # /cart
└── layout.tsx
```

### Parallel Routes

```
app/
├── @modal/
│   └── login/page.tsx     # Parallel route
├── @sidebar/
│   └── page.tsx
├── layout.tsx             # Receives both as props
└── page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
  sidebar,
}: {
  children: React.ReactNode
  modal: React.ReactNode
  sidebar: React.ReactNode
}) {
  return (
    <div>
      {sidebar}
      {children}
      {modal}
    </div>
  )
}
```

## Layouts

### Root Layout (Required)

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'My App',
  description: 'My app description',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav>Navigation</nav>
        <main>{children}</main>
        <footer>Footer</footer>
      </body>
    </html>
  )
}
```

### Nested Layouts

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="dashboard">
      <aside>Sidebar</aside>
      <section>{children}</section>
    </div>
  )
}
```

## Server Components vs Client Components

### Server Components (Default)

```tsx
// app/posts/page.tsx - Server Component by default
import { db } from '@/lib/db'

export default async function Posts() {
  // Can directly access database
  const posts = await db.posts.findMany()

  // Can use environment variables safely
  const apiKey = process.env.API_KEY

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

**When to use Server Components:**
- Fetch data from database/API
- Access backend resources directly
- Keep sensitive information on server
- Reduce client-side JavaScript

### Client Components

```tsx
// app/components/counter.tsx
'use client'

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>
        Increment
      </button>
    </div>
  )
}
```

**When to use Client Components:**
- Event handlers (onClick, onChange)
- State management (useState, useReducer)
- Lifecycle effects (useEffect)
- Browser APIs (localStorage, window)
- Custom hooks with state

### Mixing Server and Client Components

```tsx
// app/page.tsx (Server Component)
import Counter from './components/counter'  // Client Component
import { getPosts } from '@/lib/data'

export default async function Page() {
  const posts = await getPosts()  // Server-side fetch

  return (
    <div>
      <h1>My Page</h1>
      {/* Server-rendered data */}
      <ul>
        {posts.map(post => <li key={post.id}>{post.title}</li>)}
      </ul>
      {/* Client component for interactivity */}
      <Counter />
    </div>
  )
}
```

### Passing Server Data to Client Components

```tsx
// app/page.tsx (Server)
import LikeButton from './components/like-button'

export default async function Page() {
  const post = await getPost(1)

  return (
    <div>
      <h1>{post.title}</h1>
      {/* Pass serializable data as props */}
      <LikeButton initialLikes={post.likes} postId={post.id} />
    </div>
  )
}
```

```tsx
// app/components/like-button.tsx (Client)
'use client'

import { useState } from 'react'

export default function LikeButton({
  initialLikes,
  postId,
}: {
  initialLikes: number
  postId: number
}) {
  const [likes, setLikes] = useState(initialLikes)

  return (
    <button onClick={() => setLikes(likes + 1)}>
      ❤️ {likes}
    </button>
  )
}
```

## Data Fetching

### Server Component Fetching

```tsx
// app/posts/page.tsx
async function getPosts() {
  const res = await fetch('https://api.example.com/posts', {
    // Cache options
    cache: 'force-cache',  // Default - cache indefinitely
    // cache: 'no-store',  // Don't cache
    // next: { revalidate: 60 },  // Revalidate every 60 seconds
  })

  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export default async function Posts() {
  const posts = await getPosts()

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  )
}
```

### Parallel Data Fetching

```tsx
// app/dashboard/page.tsx
async function getUser(id: string) {
  const res = await fetch(`/api/users/${id}`)
  return res.json()
}

async function getPosts(userId: string) {
  const res = await fetch(`/api/users/${userId}/posts`)
  return res.json()
}

export default async function Dashboard({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  // Fetch in parallel
  const [user, posts] = await Promise.all([
    getUser(id),
    getPosts(id),
  ])

  return (
    <div>
      <h1>{user.name}</h1>
      <ul>
        {posts.map(post => <li key={post.id}>{post.title}</li>)}
      </ul>
    </div>
  )
}
```

### Client-Side Fetching (SWR)

```tsx
'use client'

import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function Profile() {
  const { data, error, isLoading } = useSWR('/api/user', fetcher)

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error loading data</div>

  return <div>Hello, {data.name}!</div>
}
```

### Streaming with Suspense

```tsx
// app/page.tsx
import { Suspense } from 'react'
import Posts from './posts'
import PostsSkeleton from './posts-skeleton'

export default function Page() {
  return (
    <div>
      <h1>My Blog</h1>
      {/* Stream posts as they load */}
      <Suspense fallback={<PostsSkeleton />}>
        <Posts />
      </Suspense>
    </div>
  )
}
```

```tsx
// app/posts.tsx (Server Component)
async function getPosts() {
  // Slow API call
  await new Promise(resolve => setTimeout(resolve, 2000))
  return [{ id: 1, title: 'Post 1' }]
}

export default async function Posts() {
  const posts = await getPosts()

  return (
    <ul>
      {posts.map(post => <li key={post.id}>{post.title}</li>)}
    </ul>
  )
}
```

## Server Actions

### Creating Server Actions

```tsx
// app/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { db } from '@/lib/db'

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string
  const content = formData.get('content') as string

  await db.posts.create({
    data: { title, content },
  })

  revalidatePath('/posts')
  redirect('/posts')
}

export async function deletePost(id: number) {
  await db.posts.delete({ where: { id } })
  revalidatePath('/posts')
}

export async function updatePost(id: number, formData: FormData) {
  const title = formData.get('title') as string

  await db.posts.update({
    where: { id },
    data: { title },
  })

  revalidatePath('/posts')
}
```

### Using Server Actions in Forms

```tsx
// app/posts/new/page.tsx
import { createPost } from '@/app/actions'

export default function NewPost() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

### Server Actions with Client Components

```tsx
// app/components/delete-button.tsx
'use client'

import { deletePost } from '@/app/actions'

export default function DeleteButton({ postId }: { postId: number }) {
  return (
    <button onClick={() => deletePost(postId)}>
      Delete
    </button>
  )
}
```

### Server Actions with useActionState (React 19)

```tsx
// app/components/create-form.tsx
'use client'

import { useActionState } from 'react'
import { createPost } from '@/app/actions'

export default function CreateForm() {
  const [error, formAction, isPending] = useActionState(
    async (prevState: string | null, formData: FormData) => {
      try {
        await createPost(formData)
        return null
      } catch (e) {
        return 'Failed to create post'
      }
    },
    null
  )

  return (
    <form action={formAction}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creating...' : 'Create Post'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}
```

## React 19 Features

### useActionState

```tsx
'use client'

import { useActionState } from 'react'

async function updateName(prevState: any, formData: FormData) {
  const name = formData.get('name')
  // Server mutation
  const error = await saveName(name)
  if (error) return { error }
  return { success: true }
}

export default function UpdateForm() {
  const [state, formAction, isPending] = useActionState(updateName, null)

  return (
    <form action={formAction}>
      <input name="name" />
      <button disabled={isPending}>
        {isPending ? 'Updating...' : 'Update'}
      </button>
      {state?.error && <p>{state.error}</p>}
    </form>
  )
}
```

### useFormStatus

```tsx
'use client'

import { useFormStatus } from 'react-dom'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  )
}

export default function Form() {
  return (
    <form action={serverAction}>
      <input name="email" />
      <SubmitButton />
    </form>
  )
}
```

### useOptimistic

```tsx
'use client'

import { useOptimistic } from 'react'

export default function Messages({
  messages,
}: {
  messages: { id: number; text: string }[]
}) {
  const [optimisticMessages, addOptimisticMessage] = useOptimistic(
    messages,
    (state, newMessage: string) => [
      ...state,
      { id: Date.now(), text: newMessage },
    ]
  )

  async function sendMessage(formData: FormData) {
    const text = formData.get('text') as string
    addOptimisticMessage(text)  // Show immediately
    await saveMessage(text)      // Actually save
  }

  return (
    <div>
      <ul>
        {optimisticMessages.map(msg => (
          <li key={msg.id}>{msg.text}</li>
        ))}
      </ul>
      <form action={sendMessage}>
        <input name="text" />
        <button>Send</button>
      </form>
    </div>
  )
}
```

### use Hook

```tsx
'use client'

import { use, Suspense } from 'react'

function Comments({ commentsPromise }: { commentsPromise: Promise<any[]> }) {
  // Suspends until promise resolves
  const comments = use(commentsPromise)

  return (
    <ul>
      {comments.map(comment => (
        <li key={comment.id}>{comment.text}</li>
      ))}
    </ul>
  )
}

// Conditional context reading
function Header({ showTitle }: { showTitle: boolean }) {
  if (!showTitle) return null

  const theme = use(ThemeContext)  // Can use after early return!
  return <h1 style={{ color: theme.color }}>Title</h1>
}

export default function Page() {
  const commentsPromise = fetchComments()

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Comments commentsPromise={commentsPromise} />
    </Suspense>
  )
}
```

### ref as Prop (No forwardRef needed)

```tsx
// React 19 - ref is now a regular prop
function Input({ placeholder, ref }: {
  placeholder: string
  ref: React.Ref<HTMLInputElement>
}) {
  return <input placeholder={placeholder} ref={ref} />
}

// Usage
function Form() {
  const inputRef = useRef<HTMLInputElement>(null)
  return <Input placeholder="Enter text" ref={inputRef} />
}
```

### Context as Provider

```tsx
// React 19 - Use context directly as provider
const ThemeContext = createContext('light')

// Before
<ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>

// After (React 19)
<ThemeContext value="dark">{children}</ThemeContext>
```

## Navigation

### Link Component

```tsx
import Link from 'next/link'

export default function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/blog/my-post">Blog Post</Link>
      <Link href={{ pathname: '/blog', query: { page: '1' } }}>
        Blog Page 1
      </Link>
    </nav>
  )
}
```

### useRouter Hook

```tsx
'use client'

import { useRouter, usePathname, useSearchParams } from 'next/navigation'

export default function Navigation() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  return (
    <div>
      <p>Current path: {pathname}</p>
      <p>Query: {searchParams.get('q')}</p>
      <button onClick={() => router.push('/dashboard')}>
        Go to Dashboard
      </button>
      <button onClick={() => router.back()}>Go Back</button>
      <button onClick={() => router.refresh()}>Refresh</button>
    </div>
  )
}
```

### Redirect

```tsx
// In Server Component
import { redirect } from 'next/navigation'

export default async function Page() {
  const user = await getUser()

  if (!user) {
    redirect('/login')
  }

  return <div>Welcome, {user.name}</div>
}

// In Server Action
'use server'

import { redirect } from 'next/navigation'

export async function createPost(formData: FormData) {
  await savePost(formData)
  redirect('/posts')
}
```

## Loading & Error States

### Loading UI

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="loading">
      <div className="spinner" />
      <p>Loading...</p>
    </div>
  )
}
```

### Error Handling

```tsx
// app/dashboard/error.tsx
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  )
}
```

### Not Found

```tsx
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>Could not find the requested resource</p>
      <Link href="/">Return Home</Link>
    </div>
  )
}
```

```tsx
// Triggering not-found programmatically
import { notFound } from 'next/navigation'

export default async function Page({ params }: { params: { id: string } }) {
  const post = await getPost(params.id)

  if (!post) {
    notFound()
  }

  return <div>{post.title}</div>
}
```

## API Routes

### Route Handlers

```tsx
// app/api/posts/route.ts
import { NextResponse } from 'next/server'

// GET /api/posts
export async function GET() {
  const posts = await db.posts.findMany()
  return NextResponse.json(posts)
}

// POST /api/posts
export async function POST(request: Request) {
  const body = await request.json()
  const post = await db.posts.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

### Dynamic Route Handlers

```tsx
// app/api/posts/[id]/route.ts
import { NextResponse } from 'next/server'

// GET /api/posts/123
export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const post = await db.posts.findUnique({ where: { id: parseInt(id) } })

  if (!post) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 })
  }

  return NextResponse.json(post)
}

// DELETE /api/posts/123
export async function DELETE(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  await db.posts.delete({ where: { id: parseInt(id) } })
  return new Response(null, { status: 204 })
}
```

### Request Helpers

```tsx
// app/api/search/route.ts
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get('q')
  const page = searchParams.get('page') || '1'

  // Access headers
  const authHeader = request.headers.get('Authorization')

  // Access cookies
  const cookies = request.headers.get('Cookie')

  const results = await search(query, parseInt(page))
  return NextResponse.json(results)
}
```

## Middleware (Proxy)

```tsx
// middleware.ts (or proxy.ts in Next.js 16+)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check auth
  const token = request.cookies.get('token')

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Add headers
  const response = NextResponse.next()
  response.headers.set('x-custom-header', 'my-value')

  return response
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*'],
}
```

## Metadata & SEO

### Static Metadata

```tsx
// app/layout.tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: 'My App',
    template: '%s | My App',
  },
  description: 'My app description',
  keywords: ['Next.js', 'React', 'TypeScript'],
  authors: [{ name: 'John Doe' }],
  openGraph: {
    title: 'My App',
    description: 'My app description',
    url: 'https://myapp.com',
    siteName: 'My App',
    images: [
      {
        url: 'https://myapp.com/og.jpg',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My App',
    description: 'My app description',
    images: ['https://myapp.com/og.jpg'],
  },
}
```

### Dynamic Metadata

```tsx
// app/blog/[slug]/page.tsx
import type { Metadata } from 'next'

type Props = {
  params: Promise<{ slug: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [post.image],
    },
  }
}
```

## Environment Variables

```bash
# .env.local
DATABASE_URL=postgresql://...
API_KEY=secret123

# Public (exposed to browser)
NEXT_PUBLIC_API_URL=https://api.example.com
```

```tsx
// Server-side only
const dbUrl = process.env.DATABASE_URL

// Client-side (must have NEXT_PUBLIC_ prefix)
const apiUrl = process.env.NEXT_PUBLIC_API_URL
```

## Image Optimization

```tsx
import Image from 'next/image'

export default function Page() {
  return (
    <div>
      {/* Local image */}
      <Image
        src="/hero.jpg"
        alt="Hero"
        width={1200}
        height={600}
        priority  // Preload for LCP
      />

      {/* Remote image */}
      <Image
        src="https://example.com/photo.jpg"
        alt="Photo"
        width={400}
        height={300}
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,..."
      />

      {/* Fill container */}
      <div style={{ position: 'relative', width: '100%', height: '400px' }}>
        <Image
          src="/banner.jpg"
          alt="Banner"
          fill
          style={{ objectFit: 'cover' }}
        />
      </div>
    </div>
  )
}
```

## Fonts

```tsx
// app/layout.tsx
import { Inter, Roboto_Mono } from 'next/font/google'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  variable: '--font-roboto-mono',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${robotoMono.variable}`}>
      <body>{children}</body>
    </html>
  )
}
```

## Caching & Revalidation

### Static Generation (Default)

```tsx
// Statically generated at build time
export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}
```

### Time-Based Revalidation

```tsx
// Revalidate every 60 seconds
export const revalidate = 60

export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data}</div>
}

// Or per-fetch
const data = await fetch('https://api.example.com/data', {
  next: { revalidate: 60 },
})
```

### On-Demand Revalidation

```tsx
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache'

export async function POST(request: Request) {
  const { path, tag } = await request.json()

  if (path) {
    revalidatePath(path)
  }

  if (tag) {
    revalidateTag(tag)
  }

  return Response.json({ revalidated: true })
}
```

### Dynamic Rendering

```tsx
// Force dynamic rendering
export const dynamic = 'force-dynamic'

// Or use no-store fetch
const data = await fetch('https://api.example.com/data', {
  cache: 'no-store',
})
```

## Best Practices

### 1. Component Organization

```
components/
├── ui/                    # Reusable UI components
│   ├── button.tsx
│   ├── input.tsx
│   └── card.tsx
├── forms/                 # Form components
│   ├── login-form.tsx
│   └── signup-form.tsx
└── layout/                # Layout components
    ├── header.tsx
    ├── footer.tsx
    └── sidebar.tsx
```

### 2. Server vs Client Decision

```tsx
// Default to Server Components
// Only add 'use client' when you need:
// - useState, useEffect
// - Event handlers (onClick, onChange)
// - Browser APIs

// ✅ Good: Fetch data in Server Component
async function Posts() {
  const posts = await getPosts()
  return <PostList posts={posts} />
}

// ✅ Good: Small Client Component for interactivity
'use client'
function LikeButton({ postId }: { postId: number }) {
  const [liked, setLiked] = useState(false)
  return <button onClick={() => setLiked(!liked)}>Like</button>
}
```

### 3. Data Fetching Patterns

```tsx
// ✅ Parallel fetching
const [user, posts] = await Promise.all([
  getUser(id),
  getPosts(id),
])

// ✅ Streaming with Suspense
<Suspense fallback={<Loading />}>
  <SlowComponent />
</Suspense>

// ✅ Preload data
import { preload } from '@/lib/data'
preload(id)  // Start loading early
```

### 4. Error Handling

```tsx
// Use error.tsx for route-level errors
// Use try-catch in Server Actions
'use server'

export async function createPost(formData: FormData) {
  try {
    await db.posts.create({ data: formData })
    revalidatePath('/posts')
  } catch (error) {
    return { error: 'Failed to create post' }
  }
}
```

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Page | `app/*/page.tsx` | Route UI |
| Layout | `app/*/layout.tsx` | Shared wrapper |
| Loading | `app/*/loading.tsx` | Suspense fallback |
| Error | `app/*/error.tsx` | Error boundary |
| API | `app/api/*/route.ts` | HTTP handlers |
| Actions | `'use server'` | Server mutations |
| Client | `'use client'` | Browser interactivity |

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [App Router Docs](https://nextjs.org/docs/app)
- [Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations)
