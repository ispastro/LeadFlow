import { useState, useEffect } from 'react'

function StreamingText({ text, isAnimating, speed = 15 }) {
  const [displayedText, setDisplayedText] = useState('')

  useEffect(() => {
    if (!isAnimating) {
      setDisplayedText(text)
      return
    }

    let currentIndex = 0
    setDisplayedText('')

    const interval = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1))
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, isAnimating, speed])

  return <span>{displayedText}</span>
}

export default StreamingText
