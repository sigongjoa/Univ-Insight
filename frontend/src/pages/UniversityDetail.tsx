
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { universityService, type University, type Paper } from '../services/universityService'
import './UniversityDetail.css'

export default function UniversityDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [university, setUniversity] = useState<University | null>(null)
    const [loading, setLoading] = useState(true)
    const [crawlUrl, setCrawlUrl] = useState('')
    const [crawling, setCrawling] = useState(false)
    const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error' | 'info', text: string } | null>(null)
    const [papers, setPapers] = useState<Paper[]>([])
    const [loadingPapers, setLoadingPapers] = useState(false)

    useEffect(() => {
        if (id) {
            loadUniversity(id)
            loadPapers(id)
        }
    }, [id])

    const loadUniversity = async (uniId: string) => {
        try {
            const data = await universityService.getUniversity(uniId)
            setUniversity(data)
            setCrawlUrl(data.url || '')
        } catch (error) {
            console.error("Failed to load university:", error)
            setStatusMessage({ type: 'error', text: 'Failed to load university details' })
        } finally {
            setLoading(false)
        }
    }

    const loadPapers = async (uniId: string) => {
        setLoadingPapers(true)
        try {
            const data = await universityService.getPapers(uniId)
            setPapers(data.items)
        } catch (error) {
            console.error("Failed to load papers:", error)
        } finally {
            setLoadingPapers(false)
        }
    }

    const handleCrawl = async () => {
        if (!id || !crawlUrl) return

        setCrawling(true)
        setStatusMessage({ type: 'info', text: 'Starting crawl job...' })

        try {
            const result = await universityService.crawlUniversity(id, crawlUrl)
            setStatusMessage({
                type: 'success',
                text: `Crawl job queued successfully! Status: ${result.status}. Refresh papers in a few moments.`
            })
        } catch (error) {
            console.error("Failed to start crawl:", error)
            setStatusMessage({ type: 'error', text: 'Failed to start crawl job' })
        } finally {
            setCrawling(false)
        }
    }

    const handleRefreshPapers = () => {
        if (id) {
            loadPapers(id)
            setStatusMessage({ type: 'info', text: 'Refreshing papers...' })
        }
    }

    if (loading) {
        return <div className="university-detail-container">Loading...</div>
    }

    if (!university) {
        return <div className="university-detail-container">University not found</div>
    }

    return (
        <div className="university-detail-container">
            <button className="back-button" onClick={() => navigate('/universities')}>
                ← Back to List
            </button>

            <div className="uni-header">
                <h1>{university.name_ko}</h1>
                <p>{university.name}</p>
            </div>

            <div className="uni-info-grid">
                <div className="info-card">
                    <h3>Location</h3>
                    <p>{university.location || 'N/A'}</p>
                </div>
                <div className="info-card">
                    <h3>Established</h3>
                    <p>{university.established_year || 'N/A'}</p>
                </div>
                <div className="info-card">
                    <h3>Tier</h3>
                    <p>{university.tier || 'N/A'}</p>
                </div>
                <div className="info-card">
                    <h3>Website</h3>
                    <p>
                        {university.url ? (
                            <a href={university.url} target="_blank" rel="noopener noreferrer">
                                Visit
                            </a>
                        ) : 'N/A'}
                    </p>
                </div>
            </div>

            <div className="crawl-section">
                <h2>🔍 Crawl University Data</h2>
                <p style={{ marginBottom: '1rem', color: '#666' }}>
                    Enter a URL to crawl research papers and information from this university.
                </p>

                <div className="crawl-form">
                    <input
                        type="url"
                        className="crawl-input"
                        placeholder="Enter URL to crawl (e.g., https://university.edu/research)"
                        value={crawlUrl}
                        onChange={e => setCrawlUrl(e.target.value)}
                    />
                    <button
                        className="crawl-button"
                        onClick={handleCrawl}
                        disabled={crawling || !crawlUrl}
                    >
                        {crawling ? 'Crawling...' : 'Start Crawl'}
                    </button>
                </div>

                {statusMessage && (
                    <div className={`status-message ${statusMessage.type}`}>
                        {statusMessage.text}
                    </div>
                )}
            </div>

            <div className="papers-section">
                <h2>📚 Crawled Papers</h2>
                <button className="refresh-button" onClick={handleRefreshPapers} disabled={loadingPapers}>
                    {loadingPapers ? 'Loading...' : '🔄 Refresh Papers'}
                </button>

                {papers.length > 0 ? (
                    <div className="papers-list">
                        {papers.map(paper => (
                            <div key={paper.id} className="paper-card">
                                <h3 className="paper-title">{paper.title}</h3>
                                {paper.abstract && (
                                    <p className="paper-abstract">{paper.abstract}</p>
                                )}
                                <div className="paper-meta">
                                    {paper.url && (
                                        <a href={paper.url} target="_blank" rel="noopener noreferrer">
                                            🔗 View Paper
                                        </a>
                                    )}
                                    {paper.crawled_at && (
                                        <span>📅 Crawled: {new Date(paper.crawled_at).toLocaleDateString()}</span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="no-papers">
                        No papers crawled yet. Start a crawl job above to see results here.
                    </div>
                )}
            </div>
        </div>
    )
}
