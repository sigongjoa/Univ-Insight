
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { universityService, type University } from '../services/universityService'
import './UniversityList.css'

export default function UniversityList() {
    const [universities, setUniversities] = useState<University[]>([])
    const [loading, setLoading] = useState(true)
    const [searchTerm, setSearchTerm] = useState('')
    const navigate = useNavigate()

    useEffect(() => {
        loadUniversities()
    }, [])

    const loadUniversities = async () => {
        try {
            const data = await universityService.getUniversities()
            setUniversities(data.items)
        } catch (error) {
            console.error("Failed to load universities:", error)
        } finally {
            setLoading(false)
        }
    }

    const filtered = universities.filter(u =>
        u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.name_ko.includes(searchTerm)
    )

    return (
        <div className="university-list-container">
            <h1 className="page-title">University Explorer</h1>
            <input
                type="text"
                placeholder="Search universities by name (Korean or English)..."
                className="search-bar"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
            />

            {loading ? (
                <div className="loading-spinner">Loading universities...</div>
            ) : (
                <div className="university-grid">
                    {filtered.map(uni => (
                        <div
                            key={uni.id}
                            className="university-card"
                            onClick={() => navigate(`/universities/${uni.id}`)}
                        >
                            <h2 className="uni-name-ko">{uni.name_ko}</h2>
                            <p className="uni-name-en">{uni.name}</p>
                            <p className="uni-location">📍 {uni.location || 'Location not available'}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
