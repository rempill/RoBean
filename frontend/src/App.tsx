import { useState, useEffect, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import CoffeeCard from '@/components/CoffeeCard';
import { Bean } from '@/types';

function App() {
    const [beans, setBeans] = useState<Bean[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState<'default' | 'cheapest'>('default');

    useEffect(() => {
        const fetchUrl = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/beans` : '/api/beans';
        fetch(fetchUrl)
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                let allBeans: Bean[] = [];
                if (data?.stores) {
                    data.stores.forEach((store: any) => {
                        (store.beans || []).forEach((bean: any) => {
                            allBeans.push({
                                id: bean.id,
                                storeId: store.id,
                                storeName: store.name,
                                storeUrl: store.url || '',
                                name: bean.name,
                                url: bean.url,
                                imageUrl: bean.image || bean.imageUrl,
                                first_seen_at: bean.first_seen_at,
                                variants: (bean.variants || []).map((v: any) => ({
                                    id: v.id,
                                    weightGrams: v.weight_grams || v.weightGrams,
                                    price: v.price,
                                    pricePerGram: v.price_per_gram || v.pricePerGram
                                }))
                            });
                        });
                    });
                } else if (Array.isArray(data)) {
                    allBeans = data.map((bean: any) => ({
                        ...bean,
                        storeUrl: bean.storeUrl || '',
                        imageUrl: bean.image || bean.imageUrl,
                        variants: (bean.variants || []).map((v: any) => ({
                            ...v,
                            weightGrams: v.weight_grams || v.weightGrams,
                            pricePerGram: v.price_per_gram || v.pricePerGram
                        }))
                    }));
                }
                setBeans(allBeans);
            })
            .catch(err => setError(err.message))
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => {
        document.title = 'RoBean ☕';
    }, []);

    const processedBeans = useMemo(() => {
        const query = searchQuery.toLowerCase();
        let filtered = beans.filter(bean => bean.name.toLowerCase().includes(query));

        if (sortBy === 'cheapest') {
            filtered.sort((a, b) => {
                const getMinPpg = (bean: Bean) => {
                    if (!bean.variants || bean.variants.length === 0) return Infinity;
                    return Math.min(...bean.variants.map(v => v.pricePerGram).filter(n => Number.isFinite(n)));
                };
                return getMinPpg(a) - getMinPpg(b);
            });
        }
        return filtered;
    }, [beans, searchQuery, sortBy]);

    const isFlattened = searchQuery.trim() !== '' || sortBy === 'cheapest';

    const renderFlattened = () => {
        return (
            <div className="flex flex-wrap justify-center gap-4 w-full">
                {processedBeans.map((bean, index) => {
                    const isTopPick = sortBy === 'cheapest' && index === 0;

                    return (
                        <a key={`${bean.id}-${index}`} href={bean.url} className={`flex-shrink-0 w-[140px] sm:w-[180px] md:w-[200px] rounded-lg ${isTopPick ? 'ring-2 ring-yellow-400 shadow-xl' : ''}`}>
                            <div className="relative w-full h-full">
                                {isTopPick && (
                                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10 whitespace-nowrap bg-yellow-400 text-yellow-900 text-[10px] font-bold px-3 py-1 rounded-full shadow-lg border border-yellow-500 uppercase tracking-wide">
                                        Top Value Match
                                    </div>
                                )}
                                <CoffeeCard bean={bean} />
                            </div>
                        </a>
                    );
                })}
            </div>
        );
    };

    const renderGrouped = () => {
        const storeMap = new Map<string, Bean[]>();
        const urlMap = new Map<string, string>();
        
        processedBeans.forEach(bean => {
            if (!storeMap.has(bean.storeName)) {
                storeMap.set(bean.storeName, []);
                urlMap.set(bean.storeName, bean.storeUrl);
            }
            storeMap.get(bean.storeName)!.push(bean);
        });

        const storeNames = Array.from(storeMap.keys()).sort();

        return (
            <>
                {storeNames.map(storeName => {
                    const storeBeans = storeMap.get(storeName)!;
                    const storeUrl = urlMap.get(storeName);
                    
                    if (storeBeans.length === 0) return null;

                    return (
                        <section key={storeName} className="w-full">
                            <div className="flex items-center justify-between mb-2">
                                <h2 className="text-xl font-bold text-stone-800">
                                    {storeName}
                                </h2>
                                {storeUrl && (
                                    <a className="text-sm text-blue-600 hover:underline" href={storeUrl} target="_blank" rel="noreferrer">
                                        Visit store
                                    </a>
                                )}
                            </div>
                            <div className="flex flex-wrap justify-center gap-4 w-full">
                                {storeBeans.map((bean, index) => (
                                    <a key={`${bean.id}-${index}`} href={bean.url} className="flex-shrink-0 w-[140px] sm:w-[180px] md:w-[200px]">
                                        <CoffeeCard bean={bean} />
                                    </a>
                                ))}
                            </div>
                        </section>
                    );
                })}
            </>
        );
    };

    return (
        <div className="w-full p-6">
            <header className="mb-8 w-full">
                <div className="flex flex-wrap items-center justify-center lg:justify-between">
                    {/* Left: Logo + Title + Tagline */}
                    <div className="flex flex-col">
                        <a href="">
                            <div className="flex items-center gap-4">
                                <img src={'/logo.png'} alt="RoBean Logo" className="h-10 w-10" />
                                <h1 className="text-4xl font-extrabold tracking-tight text-stone-900">
                                    RoBean
                                </h1>
                            </div>
                        </a>
                        <p className="text-stone-600 mt-1">Search Smarter, Sip Better Coffee</p>
                    </div>

                    {/* Right: Search Input & Sort */}
                    <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto items-center justify-end mt-4 lg:mt-0">
                        <Input
                            type="text"
                            placeholder="Search beans..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            style={{ backgroundColor: 'rgb(223, 216, 208)' }} // 10% darker
                            onMouseEnter={e => e.currentTarget.style.backgroundColor = 'rgb(236, 228, 219)'} // 5% darker on hover
                            onMouseLeave={e => e.currentTarget.style.backgroundColor = 'rgb(223, 216, 208)'} // back to 10% darker
                            className="w-full sm:w-64 border-gray-300 rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
                        />
                        <select
                            value={sortBy}
                            onChange={e => setSortBy(e.target.value as 'default' | 'cheapest')}
                            style={{ backgroundColor: 'rgb(223, 216, 208)' }}
                            onMouseEnter={e => e.currentTarget.style.backgroundColor = 'rgb(236, 228, 219)'}
                            onMouseLeave={e => e.currentTarget.style.backgroundColor = 'rgb(223, 216, 208)'}
                            className="w-full sm:w-auto appearance-none border-transparent text-stone-700 font-medium rounded-full px-6 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200 cursor-pointer"
                        >
                            <option value="default">Sort: Default</option>
                            <option value="cheapest">Price/g: Low to High</option>
                        </select>
                    </div>
                </div>
            </header>

            {loading && <p>Loading beans... into the grinder :)</p>}
            {error && <p className="text-red-600">Failed to load: {error}</p>}

            {!loading && !error && processedBeans.length === 0 && (
                <p className="text-muted-foreground">No beans found... unless?</p>
            )}

            {!loading && !error && processedBeans.length > 0 && (
                <div className="flex flex-col px-2 sm:px-4 lg:px-8 justify-center gap-8 w-full max-w mx-auto">
                    {isFlattened ? renderFlattened() : renderGrouped()}
                </div>
            )}
        </div>
    );
}

export default App;
