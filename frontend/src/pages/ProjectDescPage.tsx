import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { config } from '../config'

interface ProjectType {
  id: string
  name: string
  description: string
  template_prompts: string[]
}

interface GeneratedContent {
  goals: string
  concept: string
  target_audience: string
  key_features: string
  timeline: string
  success_metrics: string
}

interface ImageUpload {
  image_id: string
  filename: string
  url: string
  placeholder_type: string
}

export default function ProjectDescPage() {
  const navigate = useNavigate()
  const [projectTypes, setProjectTypes] = useState<ProjectType[]>([])
  const [selectedType, setSelectedType] = useState<string>('')
  const [projectName, setProjectName] = useState('')
  const [briefDescription, setBriefDescription] = useState('')
  const [targetAudience, setTargetAudience] = useState('')
  const [stylePreference, setStylePreference] = useState('')
  
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null)
  const [images, setImages] = useState<ImageUpload[]>([])
  const [language, setLanguage] = useState<'NO' | 'EN'>('NO')
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  const [currentStep, setCurrentStep] = useState(1)
  const [uploadingImage, setUploadingImage] = useState(false)
  const [generatedPDFUrl, setGeneratedPDFUrl] = useState<string | null>(null)

  useEffect(() => {
    fetchProjectTypes()
  }, [])

  const validateToken = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      navigate('/login')
      return false
    }

    try {
      const response = await fetch(`${config.backendUrl}/healthz`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        navigate('/login')
        return false
      }

      return true
    } catch (err) {
      console.error('Token validation error:', err)
      return false
    }
  }

  const fetchProjectTypes = async () => {
    try {
      if (!(await validateToken())) {
        return
      }

      const token = localStorage.getItem('access_token')
      const response = await fetch(`${config.backendUrl}/project-types`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const types = await response.json()
        setProjectTypes(types)
      } else {
        setError('Kunne ikke hente prosjekttyper')
      }
    } catch (err) {
      setError('Feil ved henting av prosjekttyper')
    }
  }

  const generateContent = async () => {
    if (!selectedType || !projectName || !briefDescription) {
      setError('Vennligst fyll ut alle påkrevde felter')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setError('Ingen tilgangstoken funnet. Vennligst logg inn på nytt.')
        navigate('/login')
        return
      }

      console.log('🔐 Using token:', token.substring(0, 20) + '...')
      console.log('📤 Sending request to:', `${config.backendUrl}/generate-content`)

      const response = await fetch(`${config.backendUrl}/generate-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          project_type: selectedType,
          project_name: projectName,
          brief_description: briefDescription,
          target_audience: targetAudience || undefined,
          style_preference: stylePreference || undefined
        })
      })

      console.log('📥 Response status:', response.status)
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const content = await response.json()
        console.log('✅ Content generated:', content)
        setGeneratedContent(content)
        setCurrentStep(2)
        setSuccess('Innhold generert! Du kan nå legge til bilder.')
      } else {
        const errorText = await response.text()
        console.error('❌ Error response:', errorText)
        setError(`Feil ved generering av innhold: ${errorText}`)
        
        // If it's an authentication error, redirect to login
        if (response.status === 401) {
          setError('Sesjonen har utløpt. Vennligst logg inn på nytt.')
          setTimeout(() => navigate('/login'), 2000)
        }
      }
    } catch (err) {
      console.error('❌ Network error:', err)
      setError('Feil ved generering av innhold: ' + (err instanceof Error ? err.message : String(err)))
    } finally {
      setLoading(false)
    }
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>, placeholderType: string) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploadingImage(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('placeholder_type', placeholderType)

      const response = await fetch(`${config.backendUrl}/upload-image`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (response.ok) {
        const imageData = await response.json()
        setImages(prev => [...prev, imageData])
        setSuccess('Bilde lastet opp!')
      } else {
        const errorText = await response.text()
        setError(`Feil ved bildeopplasting: ${errorText}`)
      }
    } catch (err) {
      setError('Feil ved bildeopplasting')
    } finally {
      setUploadingImage(false)
    }
  }

  const removeImage = (imageId: string) => {
    setImages(prev => prev.filter(img => img.image_id !== imageId))
  }

  const generatePDF = async () => {
    if (!generatedContent || images.length === 0) {
      setError('Vennligst generer innhold og last opp minst ett bilde')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${config.backendUrl}/generate-project-description`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          project_type: selectedType,
          project_name: projectName,
          generated_content: generatedContent,
          images: images,
          language: language
        })
      })

      if (response.ok) {
        const result = await response.json()
        console.log('✅ PDF generated:', result)
        setGeneratedPDFUrl(result.pdf_url)
        setSuccess('PDF generert! Du kan nå laste den ned.')
        setCurrentStep(3)
      } else {
        const errorText = await response.text()
        setError(`Feil ved PDF-generering: ${errorText}`)
      }
    } catch (err) {
      setError('Feil ved PDF-generering: ' + (err instanceof Error ? err.message : String(err)))
    } finally {
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    if (!generatedPDFUrl) {
      setError('Ingen PDF-URL funnet')
      return
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${config.backendUrl}${generatedPDFUrl}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        // Create blob and download
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `prosjektbeskrivelse_${projectName.replace(/\s+/g, '_')}.pdf`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        setSuccess('PDF lastet ned!')
      } else {
        setError('Kunne ikke laste ned PDF')
      }
    } catch (err) {
      setError('Feil ved nedlasting: ' + (err instanceof Error ? err.message : String(err)))
    }
  }

  const resetForm = () => {
    setSelectedType('')
    setProjectName('')
    setBriefDescription('')
    setTargetAudience('')
    setStylePreference('')
    setGeneratedContent(null)
    setImages([])
    setCurrentStep(1)
    setError(null)
    setSuccess(null)
    setGeneratedPDFUrl(null)
  }

  return (
    <div style={{
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '16px',
        padding: '32px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
        border: '1px solid #e1e5e9',
        position: 'relative'
      }}>
        {/* Leafilms Logo */}
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <span style={{
            color: '#000000',
            fontWeight: '700',
            fontSize: '1.2rem',
            letterSpacing: '0.5px'
          }}>
            Leafilms
          </span>
        </div>

        <h1 style={{
          margin: '0 0 24px 0',
          color: '#2c3e50',
          fontSize: '2rem',
          fontWeight: '600',
          textAlign: 'center',
          marginTop: '20px'
        }}>
          Generer Prosjektbeskrivelse
        </h1>

        {/* Progress Steps */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          marginBottom: '32px'
        }}>
          {[1, 2, 3].map(step => (
            <div key={step} style={{
              display: 'flex',
              alignItems: 'center'
            }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: currentStep >= step ? '#3b82f6' : '#e5e7eb',
                color: currentStep >= step ? 'white' : '#6b7280',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: '600',
                marginRight: '8px'
              }}>
                {step}
              </div>
              {step < 3 && (
                <div style={{
                  width: '60px',
                  height: '2px',
                  backgroundColor: currentStep > step ? '#3b82f6' : '#e5e7eb',
                  marginRight: '8px'
                }} />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Project Setup */}
        {currentStep === 1 && (
          <div>
            <h2 style={{ marginBottom: '24px', color: '#374151' }}>1. Velg prosjekttype og beskrivelse</h2>
            
            <div style={{ display: 'grid', gap: '20px' }}>
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '500',
                  color: '#374151'
                }}>
                  Prosjekttype *
                </label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '1rem'
                  }}
                >
                  <option value="">Velg prosjekttype</option>
                  {projectTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.name} - {type.description}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '500',
                  color: '#374151'
                }}>
                  Prosjektnavn *
                </label>
                <input
                  type="text"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="F.eks. Sommerfestival 2024"
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '1rem'
                  }}
                />
              </div>

              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  fontWeight: '500',
                  color: '#374151'
                }}>
                  Kort beskrivelse *
                </label>
                <textarea
                  value={briefDescription}
                  onChange={(e) => setBriefDescription(e.target.value)}
                  placeholder="Beskriv prosjektet ditt i noen få setninger..."
                  rows={4}
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '1rem',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    Målgruppe
                  </label>
                  <input
                    type="text"
                    value={targetAudience}
                    onChange={(e) => setTargetAudience(e.target.value)}
                    placeholder="F.eks. Unge voksne 18-35"
                    style={{
                      width: '100%',
                      padding: '12px',
                      borderRadius: '8px',
                      border: '1px solid #d1d5db',
                      fontSize: '1rem'
                    }}
                  />
                </div>

                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '500',
                    color: '#374151'
                  }}>
                    Stilpreferanse
                  </label>
                  <input
                    type="text"
                    value={stylePreference}
                    onChange={(e) => setStylePreference(e.target.value)}
                    placeholder="F.eks. Moderne og minimalistisk"
                    style={{
                      width: '100%',
                      padding: '12px',
                      borderRadius: '8px',
                      border: '1px solid #d1d5db',
                      fontSize: '1rem'
                    }}
                  />
                </div>
              </div>

              <button
                onClick={generateContent}
                disabled={loading || !selectedType || !projectName || !briefDescription}
                style={{
                  padding: '14px 24px',
                  backgroundColor: loading || !selectedType || !projectName || !briefDescription ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '500',
                  cursor: loading || !selectedType || !projectName || !briefDescription ? 'not-allowed' : 'pointer',
                  transition: 'background-color 0.2s'
                }}
              >
                {loading ? 'Genererer innhold...' : 'Generer innhold med AI'}
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Content Review and Images */}
        {currentStep === 2 && generatedContent && (
          <div>
            <h2 style={{ marginBottom: '24px', color: '#374151' }}>2. Gjennomgå innhold og legg til bilder</h2>
            
            {/* Generated Content Display */}
            <div style={{
              backgroundColor: '#f8fafc',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '24px'
            }}>
              <h3 style={{ marginBottom: '16px', color: '#1e293b' }}>Generert innhold:</h3>
              <div style={{ display: 'grid', gap: '16px' }}>
                <div>
                  <strong>Mål:</strong> {generatedContent.goals}
                </div>
                <div>
                  <strong>Konsept:</strong> {generatedContent.concept}
                </div>
                <div>
                  <strong>Målgruppe:</strong> {generatedContent.target_audience}
                </div>
                <div>
                  <strong>Nøkkelfunksjoner:</strong> {generatedContent.key_features}
                </div>
                <div>
                  <strong>Tidsplan:</strong> {generatedContent.timeline}
                </div>
                <div>
                  <strong>Suksesskriterier:</strong> {generatedContent.success_metrics}
                </div>
              </div>
            </div>

            {/* Image Upload Section */}
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ marginBottom: '16px', color: '#1e293b' }}>Legg til bilder:</h3>
              
              {/* Layout Preview */}
              <div style={{ 
                backgroundColor: '#f8fafc', 
                padding: '20px', 
                borderRadius: '12px', 
                marginBottom: '20px',
                border: '2px dashed #d1d5db'
              }}>
                <h4 style={{ marginBottom: '16px', color: '#374151', textAlign: 'center' }}>
                  📐 Layout Forhåndsvisning
                </h4>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '20px',
                  maxWidth: '600px',
                  margin: '0 auto'
                }}>
                  {/* Left Column - Content */}
                  <div style={{
                    backgroundColor: '#e5e7eb',
                    padding: '15px',
                    borderRadius: '8px',
                    minHeight: '200px',
                    border: '2px solid #9ca3af'
                  }}>
                    <div style={{ textAlign: 'center', marginBottom: '10px' }}>
                      <strong style={{ color: '#374151' }}>📝 Innhold</strong>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', lineHeight: '1.4' }}>
                      <div>• Mål</div>
                      <div>• Konsept</div>
                      <div>• Målgruppe</div>
                      <div>• Nøkkelfunksjoner</div>
                      <div>• Tidsplan</div>
                      <div>• Suksesskriterier</div>
                    </div>
                  </div>
                  
                  {/* Right Column - Images */}
                  <div style={{
                    backgroundColor: '#e5e7eb',
                    padding: '15px',
                    borderRadius: '8px',
                    minHeight: '200px',
                    border: '2px solid #9ca3af'
                  }}>
                    <div style={{ textAlign: 'center', marginBottom: '10px' }}>
                      <strong style={{ color: '#374151' }}>🖼️ Bilder</strong>
                    </div>
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: '1fr 1fr', 
                      gap: '10px',
                      fontSize: '0.7rem'
                    }}>
                      <div style={{
                        backgroundColor: '#f3f4f6',
                        padding: '8px',
                        borderRadius: '6px',
                        textAlign: 'center',
                        border: '1px solid #d1d5db'
                      }}>
                        Header
                      </div>
                      <div style={{
                        backgroundColor: '#f3f4f6',
                        padding: '8px',
                        borderRadius: '6px',
                        textAlign: 'center',
                        border: '1px solid #d1d5db'
                      }}>
                        Content
                      </div>
                      <div style={{
                        backgroundColor: '#f3f4f6',
                        padding: '8px',
                        borderRadius: '6px',
                        textAlign: 'center',
                        border: '1px solid #d1d5db'
                      }}>
                        Footer
                      </div>
                      <div style={{
                        backgroundColor: '#f3f4f6',
                        padding: '8px',
                        borderRadius: '6px',
                        textAlign: 'center',
                        border: '1px solid #d1d5db'
                      }}>
                        Extra
                      </div>
                    </div>
                  </div>
                </div>
                <div style={{ 
                  textAlign: 'center', 
                  marginTop: '15px', 
                  fontSize: '0.9rem', 
                  color: '#6b7280',
                  fontStyle: 'italic'
                }}>
                  PDF-en vil bli generert i landscape-format med profesjonell layout
                </div>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                {['header', 'content', 'footer'].map(placeholderType => (
                  <div key={placeholderType} style={{
                    border: '2px dashed #d1d5db',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    backgroundColor: '#f9fafb',
                    transition: 'all 0.2s ease'
                  }}>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ textTransform: 'capitalize' }}>{placeholderType}</strong>
                    </div>
                    <div style={{ 
                      fontSize: '0.8rem', 
                      color: '#6b7280', 
                      marginBottom: '12px',
                      fontStyle: 'italic'
                    }}>
                      {placeholderType === 'header' && 'Toppbilde for dokumentet'}
                      {placeholderType === 'content' && 'Hovedbilde for innhold'}
                      {placeholderType === 'footer' && 'Avsluttende bilde'}
                    </div>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => handleImageUpload(e, placeholderType)}
                      style={{ display: 'none' }}
                      id={`upload-${placeholderType}`}
                    />
                    <label
                      htmlFor={`upload-${placeholderType}`}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#3b82f6',
                        color: 'white',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.9rem',
                        transition: 'background-color 0.2s'
                      }}
                    >
                      {uploadingImage ? 'Laster opp...' : 'Velg bilde'}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Uploaded Images */}
            {images.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ marginBottom: '16px', color: '#1e293b' }}>Opplastede bilder:</h3>
                
                {/* PDF Layout Preview with Images */}
                <div style={{ 
                  backgroundColor: '#f8fafc', 
                  padding: '20px', 
                  borderRadius: '12px', 
                  marginBottom: '20px',
                  border: '1px solid #e5e7eb'
                }}>
                  <h4 style={{ marginBottom: '16px', color: '#374151', textAlign: 'center' }}>
                    🎯 Så vil PDF-en se ut:
                  </h4>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '20px',
                    maxWidth: '700px',
                    margin: '0 auto'
                  }}>
                    {/* Left Column - Content Preview */}
                    <div style={{
                      backgroundColor: '#ffffff',
                      padding: '15px',
                      borderRadius: '8px',
                      border: '2px solid #3b82f6',
                      minHeight: '250px'
                    }}>
                      <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                        <strong style={{ color: '#1e40af', fontSize: '1.1rem' }}>📝 Innhold</strong>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#374151', lineHeight: '1.4' }}>
                        <div style={{ marginBottom: '8px' }}>• <strong>Mål:</strong> {generatedContent?.goals?.substring(0, 50)}...</div>
                        <div style={{ marginBottom: '8px' }}>• <strong>Konsept:</strong> {generatedContent?.concept?.substring(0, 50)}...</div>
                        <div style={{ marginBottom: '8px' }}>• <strong>Målgruppe:</strong> {generatedContent?.target_audience?.substring(0, 50)}...</div>
                        <div style={{ marginBottom: '8px' }}>• <strong>Nøkkelfunksjoner:</strong> {generatedContent?.key_features?.substring(0, 50)}...</div>
                        <div style={{ marginBottom: '8px' }}>• <strong>Tidsplan:</strong> {generatedContent?.timeline?.substring(0, 50)}...</div>
                        <div style={{ marginBottom: '8px' }}>• <strong>Suksesskriterier:</strong> {generatedContent?.success_metrics?.substring(0, 50)}...</div>
                      </div>
                    </div>
                    
                    {/* Right Column - Images Preview */}
                    <div style={{
                      backgroundColor: '#ffffff',
                      padding: '15px',
                      borderRadius: '8px',
                      border: '2px solid #10b981',
                      minHeight: '250px'
                    }}>
                      <div style={{ textAlign: 'center', marginBottom: '15px' }}>
                        <strong style={{ color: '#059669', fontSize: '1.1rem' }}>🖼️ Bilder</strong>
                      </div>
                      <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: '1fr 1fr', 
                        gap: '8px'
                      }}>
                        {images.map((image) => (
                          <div key={image.image_id} style={{
                            position: 'relative',
                            border: '1px solid #d1d5db',
                            borderRadius: '6px',
                            overflow: 'hidden'
                          }}>
                            <img
                              src={`${config.backendUrl}${image.url}`}
                              alt={image.filename}
                              style={{
                                width: '100%',
                                height: '60px',
                                objectFit: 'cover'
                              }}
                            />
                            <div style={{
                              position: 'absolute',
                              bottom: '0',
                              left: '0',
                              right: '0',
                              backgroundColor: 'rgba(0,0,0,0.7)',
                              color: 'white',
                              fontSize: '0.6rem',
                              padding: '2px 4px',
                              textAlign: 'center'
                            }}>
                              {image.placeholder_type}
                            </div>
                          </div>
                        ))}
                        {/* Fill empty slots with placeholders */}
                        {Array.from({ length: Math.max(0, 4 - images.length) }).map((_, index) => (
                          <div key={`empty-${index}`} style={{
                            border: '1px dashed #d1d5db',
                            borderRadius: '6px',
                            height: '60px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            backgroundColor: '#f9fafb'
                          }}>
                            <span style={{ fontSize: '0.6rem', color: '#9ca3af' }}>Ledig</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div style={{ 
                    textAlign: 'center', 
                    fontSize: '0.9rem', 
                    color: '#6b7280',
                    fontStyle: 'italic'
                  }}>
                    Dette er en forhåndsvisning av layouten. PDF-en vil ha høyere oppløsning og profesjonell formatering.
                  </div>
                </div>
                
                {/* Individual Image Management */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
                  {images.map(image => (
                    <div key={image.image_id} style={{
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '12px',
                      textAlign: 'center',
                      backgroundColor: '#ffffff'
                    }}>
                      <img
                        src={`${config.backendUrl}${image.url}`}
                        alt={image.filename}
                        style={{
                          width: '100%',
                          height: '100px',
                          objectFit: 'cover',
                          borderRadius: '6px',
                          marginBottom: '8px'
                        }}
                      />
                      <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '8px' }}>
                        <strong>{image.placeholder_type}</strong>
                      </div>
                      <button
                        onClick={() => removeImage(image.image_id)}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '0.8rem',
                          cursor: 'pointer',
                          transition: 'background-color 0.2s'
                        }}
                      >
                        Fjern
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Language Selection */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '500',
                color: '#374151'
              }}>
                Språk for PDF:
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as 'NO' | 'EN')}
                style={{
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: '1px solid #d1d5db',
                  fontSize: '1rem'
                }}
              >
                <option value="NO">Norsk</option>
                <option value="EN">English</option>
              </select>
            </div>

            <div style={{ display: 'flex', gap: '16px' }}>
              <button
                onClick={() => setCurrentStep(1)}
                style={{
                  padding: '12px 20px',
                  backgroundColor: '#6b7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  cursor: 'pointer'
                }}
              >
                Tilbake
              </button>
              <button
                onClick={generatePDF}
                disabled={loading || images.length === 0}
                style={{
                  padding: '12px 20px',
                  backgroundColor: loading || images.length === 0 ? '#9ca3af' : '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '500',
                  cursor: loading || images.length === 0 ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Genererer PDF...' : 'Generer PDF'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Success */}
        {currentStep === 3 && (
          <div style={{ textAlign: 'center' }}>
            <div style={{
              fontSize: '4rem',
              marginBottom: '24px'
            }}>
              🎉
            </div>
            <h2 style={{ marginBottom: '16px', color: '#10b981' }}>
              PDF generert!
            </h2>
            <p style={{ marginBottom: '24px', color: '#6b7280' }}>
              Din prosjektbeskrivelse er klar for nedlasting.
            </p>
            <button
              onClick={resetForm}
              style={{
                padding: '12px 24px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1rem',
                cursor: 'pointer'
              }}
            >
              Lag ny prosjektbeskrivelse
            </button>
            {generatedPDFUrl && (
              <button
                onClick={downloadPDF}
                style={{
                  padding: '12px 24px',
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                  marginLeft: '10px'
                }}
              >
                Last ned PDF
              </button>
            )}
          </div>
        )}

        {/* Error and Success Messages */}
        {error && (
          <div style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '8px',
            color: '#dc2626',
            fontSize: '0.95rem'
          }}>
            ❌ {error}
          </div>
        )}

        {success && (
          <div style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#f0fdf4',
            border: '1px solid #bbf7d0',
            borderRadius: '8px',
            color: '#16a34a',
            fontSize: '0.95rem'
          }}>
            ✅ {success}
          </div>
        )}
      </div>
    </div>
  )
}


