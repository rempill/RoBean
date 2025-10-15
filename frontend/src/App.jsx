import {useState, useEffect} from 'react';
import {Input} from '@/components/ui/input';
import CoffeeCard from '@/components/coffee-card';


function App() {
    const [stores, setStores] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('');

    const queryLower = query.toLowerCase();

    useEffect(() => {
        fetch(`${import.meta.env.VITE_API_URL}/beans`)  // FastAPI endpoint
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => setStores(data?.stores ?? []))
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        document.title = 'RoBean ☕';
    }, []);

    const filteredStores = stores
        .map(store => ({
            ...store,
            beans: (store.beans ?? []).filter(b => b.name.toLowerCase().includes(queryLower))
        }))
        .filter(store => (store.beans?.length ?? 0) > 0);

    const totalBeans = filteredStores.reduce((acc, s) => acc + (s.beans?.length ?? 0), 0);

    return (
        <div className="w-full p-6">
            <header className="mb-8 w-full">
                <div className="flex flex-wrap items-center justify-center lg:justify-between">
                    {/* Left: Logo + Title + Tagline */}
                    <div className="flex flex-col">
                        <a href="">
                            <div className="flex items-center gap-4">
                                <img src={'/logo.png'} alt="RoBean Logo" className="h-10 w-10"/>
                                <h1 className="text-4xl font-extrabold tracking-tight text-stone-900">
                                    RoBean
                                </h1>
                            </div>
                        </a>
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

            {!loading && !error && totalBeans === 0 && (
                <p className="text-muted-foreground">No beans found... unless?</p>
            )}

            {!loading && !error && totalBeans > 0 && (
                <div className="flex flex-col justify-center gap-8 w-full max-w-screen-xl mx-auto">
                    {filteredStores.map(store => (
                        <section key={store.id} className="w-full">
                            <div className="flex items-center justify-between mb-2">
                                <h2 className="text-xl font-bold text-stone-800">
                                    {store.name}
                                </h2>
                                {store.url && (
                                    <a className="text-sm text-blue-600 hover:underline" href={store.url} target="_blank" rel="noreferrer">
                                        Visit store
                                    </a>
                                )}
                            </div>
                            <div className="flex flex-wrap justify-center gap-4 w-full">
                                {store.beans.map(bean => {
                                    // Compute the smallest variant price (coerce to numbers and filter invalid)
                                    const prices = (bean.variants ?? [])
                                        .map(v =>  v.price)
                                        .filter(n => Number.isFinite(n));
                                    const minPrice = prices.length ? Math.min(...prices) : undefined;

                                    return (
                                        <a key={bean.id} href={bean.url}>
                                            <div className="flex-shrink-0 w-[140px] sm:w-[180px] md:w-[200px]">
                                                <CoffeeCard
                                                    name={bean.name}
                                                    imageUrl={bean.image}
                                                    minPrice={minPrice}
                                                />
                                            </div>
                                        </a>
                                    );
                                })}
                            </div>
                        </section>
                    ))}
                </div>
            )}
        </div>
    );
}

export default App;
