export const formatDateTime = (dateString: string | null | undefined): string => {
  if (!dateString) {
    return ''
  }

  const date = new Date(dateString)

  if (isNaN(date.getTime())) {
    return 'Invalid date'
  }

  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

export const formatDuration = (totalSeconds: number | null | undefined): string => {
  if (totalSeconds === null || totalSeconds === undefined) {
    return '00:00:00'
  }

  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  return [
    hours.toString().padStart(2, '0'),
    minutes.toString().padStart(2, '0'),
    seconds.toString().padStart(2, '0'),
  ].join(':')
}
