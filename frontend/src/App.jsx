import {useState, useEffect} from 'react';
import {Input} from '@/components/ui/input';
import CoffeeCard from '@/components/coffee-card';


function App() {
    const [beans, setBeans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('');

    const filteredBeans = beans.filter(bean =>
        bean.name.toLowerCase().includes(query.toLowerCase()));

    useEffect(() => {
        console.log(import.meta.env);
        fetch(`${import.meta.env.VITE_API_URL}/beans`)  // FastAPI endpoint
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => setBeans(data.beans ?? []))
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        document.title = 'RoBean ☕';
    }, []);

    return (
        <div className="w-full p-6">
            <header className="mb-8 w-full">
                <div className="flex flex-wrap items-center justify-center lg:justify-between">
                    {/* Left: Logo + Title + Tagline */}
                    <div className="flex flex-col">
                        <div className="flex items-center gap-4">
                            <img src={'/logo.png'} alt="RoBean Logo" className="h-10 w-10"/>
                            <h1 className="text-4xl font-extrabold tracking-tight text-stone-900">
                                RoBean
                            </h1>
                        </div>
                        <p className="text-stone-600 mt-1">Search Smarter, Sip Better Coffee</p>
                    </div>

                    {/* Right: Search Input */}
                    <div className="flex flex-col w-full lg:w-1/5">
                        <Input
                            type="text"
                            placeholder="Search beans..."
                            value={query}
                            onChange={e => setQuery(e.target.value)}
                            style={{backgroundColor: 'rgb(223, 216, 208)'}} // 10% darker
                            onMouseEnter={e => e.currentTarget.style.backgroundColor = 'rgb(236, 228, 219)'} // 5% darker on hover
                            onMouseLeave={e => e.currentTarget.style.backgroundColor = 'rgb(223, 216, 208)'} // back to 10% darker
                            className="w-full border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                        />
                    </div>
                </div>
            </header>

            {loading && <p>Loading beans... into the grinder :)</p>}
            {error && <p className="text-red-600">Failed to load: {error}</p>}
            {!loading && !error && (filteredBeans.length === 0 ? (
                    <p className="text-muted-foreground">No beans found... unless?</p>
                ) : (
                    <section className="flex flex-wrap justify-center gap-4 w-full">
                        {filteredBeans.map(bean => (
                            <div className="w-[140px] lg:w-[210px]">
                                <CoffeeCard key={bean.name} name={bean.name} imageUrl={bean.image}/>
                            </div>
                        ))}
                    </section>

                )
            )}
        </div>
    );
}

export default App;
