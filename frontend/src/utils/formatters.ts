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
