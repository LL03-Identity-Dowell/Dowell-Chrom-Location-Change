import React, { use, useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';

const LIMIT = 1000 as const;

interface SearchResult {
    city: string;
    results: {
        title: string;
        snippet: string;
        link: string;
        images: { src: string }[];
    }[];
    search_content: string
}

export const Search = () => {
    const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
    const [country, setCountry] = useState('');
    const [showCountryDropdown, setShowCountryDropdown] = useState(false);
    const [allCountries, setAllCountries] = useState<string[]>([]);
    const [allLocaions, setAllLocations] = useState<string[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedLocations, setSelectedLocations] = useState<string[]>([])
    const [location, setLocation] = useState('')
    const [showLocationDropdown, setShowLocationDropdown] = useState(false)
    const [search, setSearch] = useState(false)
    const [results, setResults] = useState<SearchResult[]>([])
    const [activeIndex, setActiveIndex] = useState(0);
    const [experience, setExperience] = useState(0)
    const [coupon, setCoupon] = useState(false)
    const [couponValue, setCouponValue] = useState('')
    const [redeem, setRedeem] = useState(false)
    const [verify, setVerify] = useState(false)
    const [redeemMessage, setRedeemMessage] = useState('')

    const handleCouponChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCouponValue(e.target.value)
    }


    const [formData, setFormData] = useState({
        searchContent: '',
        numResults: 0,
        email: '',
    })
    const handleFromDataChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value,
            location: selectedLocations
        }));
        if (name === 'location') {
            setLocation(value);
            setSelectedLocations([]);
        }
    }

    const resetForm = () => {
        setFormData({
            searchContent: '',
            numResults: 0,
            email: '',
        });
        setSelectedCountries([]);
        setSelectedLocations([]);
    }



    const filteredCountries = allCountries.filter(_country => _country.toLowerCase().includes(country.toLowerCase()));

    const filteredLocations = allLocaions.filter(_location => _location.toLowerCase().includes(location.toLowerCase()));

    const indexOfLastLocation = currentPage * LIMIT;
    const indexOfFirstLocation = indexOfLastLocation - LIMIT;
    const currentLocations = filteredLocations?.slice(indexOfFirstLocation, indexOfLastLocation);


    const fetchCountries = async () => {
        try {
            const response = await axios.get('https://t9xrrt0x-8000.euw.devtunnels.ms/api/get-countries');
            setAllCountries(response.data.countries);
        } catch (error) {
            console.error('Error fetching countries:', error);
        }
    };


    const fetchLocation = async () => {
        try {
            const body = {
                "selectedCountries": selectedCountries,
                "offset": 0,
                "limit": 17000
            };
            const response = await axios.post('https://t9xrrt0x-8000.euw.devtunnels.ms/api/get-locations', body);
            if (response.status === 200) {
                const locations = response.data;
                const mergedLocations = Object.values(locations).reduce((prev: any, curr: any) =>
                    prev.concat(curr?.data?.filter((item: any) => !!item?.name).map((item: any) => item?.name))
                    , []);
                setAllLocations(mergedLocations as string[])
            }
        } catch (error) {
            console.error('Error fetching locations:', error);
        }
    };

    const handleSearch = async () => {
        try {
            setVerify(false)
            setSearch(true)
            const body = {
                "location": selectedLocations,
                "search_content": formData.searchContent,
                "num_results": formData.numResults,
                "email": formData.email,
                "occurrences": experience
            };
            const response = await axios.post('https://t9xrrt0x-8000.euw.devtunnels.ms/api/', body);
            if (response.status === 200) {

                const newSearchResults = response.data?.search_results;
                setResults(newSearchResults as SearchResult[])

                setSearch(false)
            }
        } catch (error) {
            console.error('Error fetching search results:', error);
        }
    }

    const handleRedeem = async () => {
        try {
            const response = await axios.post('https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=redeem_coupon', {
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    coupon: couponValue,
                    product_number: 'UXLIVINGLAB004'
                }),
            });


            if (response.status === 200) {
                setRedeemMessage("Redemption successful!"); // Set success message
                setRedeem(false); // Hide coupon input
                setCoupon(true); // Hide coupon input
                setCouponValue(''); // Clear coupon input
            } else {
                setRedeemMessage(response.data.message || 'Redemption failed'); // Set failure message
                setCouponValue(''); // Clear coupon input
            }
            setTimeout(() => {
                setRedeemMessage('');
            }, 5000);
        } catch (error) {
            console.error('Error while redeeming:', error);
            setRedeemMessage('Error while redeeming. Please try again.');
            setCouponValue(''); // Clear coupon input

            setTimeout(() => {
                setRedeemMessage('');
            }, 5000);
        }
    };

    const verifyUser = async () => {
        try {
            setVerify(true)
            const body = {
                "product_number": "UXLIVINGLAB004",
                "email": formData.email
            };

            const response = await axios.post('https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=register_user', body);

            if (response.status === 200) {

                const response = await axios.get(`https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=get_user_email&product_number=UXLIVINGLAB004&email=${formData.email}`);

                if (response.status === 200) {
                    const occurence = response.data?.occurrences;
                    setExperience(occurence)
                }
            }



        } catch (error) {
            console.error('Error fetching search results:', error);

        }
    }



    useEffect(() => {
        fetchCountries()

        // fetchSearchResults()
    }, [])

    useEffect(() => {
        fetchLocation()
    }, [selectedCountries])

    console.log(results?.find((_, index) => index === activeIndex))

    return (
        <div className=' w-full h-screen flex flex-col md:flex-row  '>
            <div className={`w-full md:h-full p-5 space-y-5 flex flex-col justify-center items-center md:flex-row md:space-x-20 ${verify ? 'opacity-30' : ''} `}>
                <div className="flex justify-start w-full  md:w-1/2 h-full space-y-5 flex-col items-center">
                    <div className='flex w-full justify-between md:h-[120px] p-2  items-center'>
                        <h1 className='text-[2rem] font-bold'>
                            Location specific Search
                        </h1>
                        <div className='w-[100px] h-[100px]'>
                            <img src='/company logo.png' alt="" className='w-full h-full' />
                        </div>
                    </div>
                    <div className='bg-white w-full flex p-5  space-y-5 flex-col'>
                        <form action=""
                            onSubmit={(e) => {
                                e.preventDefault()
                            }}
                            className='space-y-3 '>
                            <div className='space-y-3'>
                                <label htmlFor="">Select Country(s)</label>
                                <div
                                    className='w-full p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 relative flex gap-1 items-center flex-wrap'>
                                    <div className='flex gap-2 items-center flex-wrap'>
                                        {selectedCountries
                                            .filter((country) => country.trim().length > 0)
                                            .map((item) => (
                                                <div className='flex items-center gap-[2px] space-x-[1px] rounded-sm  bg-gray-200 border border-gray-300 p-1' key={item}>
                                                    <button
                                                        className="text-[15px] hover:bg-red-600 p-1"
                                                        onClick={() => {
                                                            setSelectedCountries((prevInputs) =>
                                                                prevInputs.filter((_item) => _item !== item)
                                                            );
                                                        }}

                                                    >
                                                        x
                                                    </button>
                                                    <p
                                                        className="text-sm p-1">
                                                        {item}
                                                    </p>
                                                </div>
                                            ))}
                                    </div>
                                    <input
                                        value={country}
                                        onClick={() => setShowCountryDropdown(prevState => !prevState)}
                                        onChange={(e) => {
                                            setCountry(e.target.value);
                                            setShowCountryDropdown(true)
                                        }}
                                        className='relative z-[10] w-full border-0 outline-0 grow' />
                                    <div className={`absolute w-full h-[auto] max-h-[350px] ${showCountryDropdown ? 'opacity-1 pointer-events-auto' : 'opacity-0 pointer-events-none'} transition-all left-0 z-[20] top-[105%] bg-white px-0 py-0 flex flex-col gap-[2px] overflow-y-auto border-2 border-gray-300 rounded-md`}>
                                        {filteredCountries.length ? filteredCountries.map((country, index) => (
                                            <button
                                                className={`w-full text-sm font-medium hover:bg-blue-400 ${selectedCountries.includes(country) ? "text-white bg-blue-400" : "text-black bg-white"} hover:text-white transition-all text-left px-1 py-2`}
                                                onClick={() => {
                                                    if (selectedCountries.length < 10 || selectedCountries.includes(country)) {
                                                        setSelectedCountries((prevCountries) => prevCountries.includes(country) ? prevCountries.filter(_country => _country !== country) : [...prevCountries, country]);
                                                        setCountry("");
                                                    }
                                                }}
                                                key={index}
                                            >
                                                {country}
                                            </button>
                                        )) : <p>No country</p>}
                                        {showCountryDropdown ? <div onClick={() => setShowCountryDropdown(false)} className="fixed w-full h-full top-0 left-0 z-[-100]" /> : null}
                                    </div>
                                </div>
                            </div>
                            <div className='space-y-3 -z-[1]'>
                                <label htmlFor="">Select Location(s)</label>
                                <div
                                    className='w-full p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 relative flex gap-1 items-center flex-wrap'>
                                    <div className='flex gap-2 items-center flex-wrap'>
                                        {selectedLocations
                                            .filter((location) => location.trim().length > 0)
                                            .map((item) => (
                                                <div className='flex items-center gap-[2px] space-x-[1px] rounded-sm  bg-gray-200 border border-gray-300 p-1 ' key={item}>
                                                    <button
                                                        className="text-[15px] hover:bg-red-600 p-1"
                                                        onClick={() => {
                                                            setSelectedLocations((prevInputs) =>
                                                                prevInputs.filter((_item) => _item !== item)
                                                            )


                                                        }}

                                                    >
                                                        x
                                                    </button>
                                                    <p
                                                        className="text-sm p-1">
                                                        {item}
                                                    </p>
                                                </div>
                                            ))}
                                    </div>
                                    <input
                                        value={location}
                                        onClick={() => setShowLocationDropdown(prevState => !prevState)}
                                        onChange={(e) => {
                                            setLocation(e.target.value);
                                            setShowLocationDropdown(true)
                                            { handleFromDataChange }

                                        }}
                                        className='relative z-[10] w-full border-0 outline-0 grow -z-0' />
                                    <div className={`absolute w-full h-[auto] max-h-[350px] ${showLocationDropdown ? 'opacity-1 pointer-events-auto' : 'opacity-0 pointer-events-none'} transition-all left-0 z-[10] top-[105%] bg-white px-0 py-0 flex flex-col gap-[2px] overflow-y-auto border-2 border-gray-300 rounded-md`}>
                                        {currentLocations.length ? currentLocations.map((location, index) => (
                                            <button
                                                className={`w-full text-sm font-medium hover:bg-blue-400 ${selectedLocations.includes(location) ? "text-white bg-blue-400" : "text-black bg-white"} hover:text-white transition-all text-left px-1 py-2`}
                                                onClick={() => {
                                                    if (selectedLocations.length < 10 || selectedLocations.includes(location)) {
                                                        setSelectedLocations((prevLocations) => prevLocations.includes(location) ? prevLocations.filter(_location => _location !== location) : [...prevLocations, location]);
                                                        setLocation("");
                                                    }
                                                }}
                                                key={index}
                                            >
                                                {location}
                                            </button>
                                        )) : <p>No location</p>}
                                        <div className="flex items-center gap-2 w-full justify-center my-8 sticky bottom-[10px] left-0">
                                            <button
                                                className={`cursor-pointer disabled:cursor-not-allowed bg-blue-500 text-white hover:bg-blue-500 hover:text-white disabled:bg-gray-300 disabled:text-gray-400 disabled:hover:bg-gray-400 disabled:hover:text-gray-500 font-normal text-base py-1 px-4 rounded-sm`}
                                                disabled={currentPage === 1}
                                                onClick={() => setCurrentPage(currentPage - 1)}
                                            >
                                                Prev
                                            </button>
                                            <p>{currentPage} of {Math.ceil(filteredLocations.length / LIMIT)}</p>
                                            <button
                                                className={`cursor-pointer disabled:cursor-not-allowed bg-blue-500 text-white hover:bg-blue-500 hover:text-white disabled:bg-gray-300 disabled:text-gray-400 disabled:hover:bg-gray-400 disabled:hover:text-gray-500 font-normal text-base py-1 px-4 rounded-sm`}
                                                disabled={currentPage === Math.ceil(filteredLocations.length / LIMIT)}
                                                onClick={() => setCurrentPage(currentPage + 1)}
                                            >
                                                Next
                                            </button>
                                        </div>
                                        {showLocationDropdown ? <div onClick={() => setShowLocationDropdown(false)} className="fixed w-full h-full top-0 left-0 z-[-100]" /> : null}
                                    </div>
                                </div>
                            </div>
                            <div className='space-y-3'>
                                <label htmlFor="searchContent">Search Keyword</label>
                                <input type="text" placeholder='Search' className='w-full p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500' name='searchContent' onChange={handleFromDataChange} required
                                />
                            </div>

                            <div className='space-y-3'>
                                <label htmlFor="numResults">Number of Results</label>
                                <input type="number" className='w-full p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500' name='numResults' onChange={handleFromDataChange} required />
                            </div>
                            <div className='space-y-3'>
                                <label htmlFor="email">Email</label>
                                <input type="email" placeholder='email' className='w-full p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500' name='email' onChange={handleFromDataChange} required
                                />
                            </div>
                            <div className='flex space-x-5 w-full'>
                                <button onClick={verifyUser} type="submit" className={`w-[100px] p-2 bg-green-700 hover:bg-green-900 text-white text-[12px] font-bold py-2 px-4 rounded focus:outline-none focus:ring focus:border-green-500 ${search ? 'cursor-not-allowed opacity-60' : ''}`}>
                                    {search ? 'Searching...' : 'Search'}
                                </button>
                                <button type="reset" className='w-[100px] p-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none text-[12px] focus:ring focus:border-red-500 ' onClick={resetForm}>Reset</button>
                            </div>

                        </form>

                        <div className='h-full w-full'>
                            <div className="bg-white rounded-lg p-4 sm:p-8 shadow-md space-y-5">
                                <h2 className="text-2xl font-semibold ">Location specific Search</h2>
                                <p>DoWell UX Living Lab will search in the web by positioning our server to the selected locations.</p>
                                <h2 className="text-2xl font-semibold ">How it works</h2>
                                <p>DoWell UX Living Lab will position the web server using the latitude and longitude of each location specified by the user and execute a search based on keywords.</p>
                                <h2 className="text-2xl font-semibold ">How to use</h2>
                                <p>Search Scenario - I am selling Yogurt, I want to analyze search results in different locations for my product.</p>
                                <p><strong>Disclaimer:</strong></p>
                                <p>We do not assume responsibility for the accuracy of the results. Variations from search engine results may occur. Use information at your own discretion.</p>


                                <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgeopositioning.uxlivinglab.online%2Fapi%2F"><img src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgeopositioning.uxlivinglab.online%2Fapi%2F&countColor=%23263759" className='mt-5' /></a>
                            </div>
                        </div>
                    </div>

                </div >

                <div className='w-full md:w-1/2 h-full flex flex-col  justify-start '>
                    <div className='flex flex-wrap max-w-full  rounded-t-lg justify-between items-center  md:max-w-full gap-2 md:min-w-[60px] max-h-[250px] min-h-[100px] border-b-[3px] pb-3 mb-10'>
                        {results.map((data, index) => (
                            <button onClick={() => setActiveIndex(index)} className={`${activeIndex === index ? "bg-[#3B82F6] text-white" : "bg-gray-400 text-black"} hover:bg-[#3B82F6] hover:text-white transition-all w-[30%] rounded-t-lg  min-h-[70px] max-h-[80px] max-w-full flex justify-center text-center px-3 py-2 items-center grow `} key={index}>
                                <span>{`${data.results.length} search results for "${formData.searchContent}" in  ${data.city}`}</span>
                            </button>
                        ))}
                    </div>



                    <div className='bg-white w-full bottom-0  p-5 max-w-full max-h-[850px] overflow-y-auto '>
                        {results?.find((_, index) => index === activeIndex)?.results?.map((result, index) => (
                            <div className='flex flex-col w-full max-h-[500px] border-b-2 p-3 space-y-4 ' key={index}>
                                <Link href={result.link} className='md:text-[25px] text-[20px] text-blue-600 hover:text-red-500' target='_blank'>{result.title}</Link>
                                <p className='md:text-[18px] text-[14px]'>{result.snippet}</p>
                                <div className='md:w-[400px] md:h-[400px] w-[200px] h-[200px] border-2'>
                                    {result.images.length ? <img src={`${result.images[0].src}`} alt="" className='w-full h-full   object-cover object-center' /> : null}
                                </div>
                            </div>

                        ))}


                    </div>

                </div>
            </div>


            <div className={`fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 shadow-sm w-[90%] md:w-[500px] min-h-[350px] max-h-[450px] bg-white rounded-md ${verify ? 'flex' : 'hidden'} justify-start items-center flex-col`}>
                <div onClick={() => {
                    setVerify(false)
                }} className='w-[20px] h-[20px] top-5 p-1 right-5 text-gray-400 font-normal rounded-md hover:text-white bg-transparent hover:bg-red-600 flex items-center absolute justify-center'>
                    X
                </div>
                <div className='flex w-full flex-col-reverse justify-between  p-2  items-center'>
                    <h1 className='text-[1.2rem] font-bold'>
                        Location specific Search
                    </h1>
                    <div className='w-[100px] h-[100px]'>
                        <img src='/company logo.png' alt="" className='w-full h-full' />
                    </div>
                </div>

                <h1>Your Experience is: {experience} </h1>
                <div className='flex w-[80%] justify-center gap-2 items-center my-10'>
                    <button className='bg-gray-400 py-2 px-4 hover:bg-red-600 text-white font-bold rounded-full' onClick={() => {
                        setVerify(false)
                    }}>
                        Cancel
                    </button>
                    <button className={`bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-full ${experience >= 6 ? "hidden" : 'flex'}`} onClick={handleSearch}>
                        Continue
                    </button>
                    <button className={`${experience >= 4 ? "flex" : 'hidden'} bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-full`}>
                        <Link href='https://dowellpay.online/contribute-payment/?product_number=UXLIVINGLAB004' target='_blank' >Contribute</Link>
                    </button>
                </div>

                <div className={`flex space-x-4 justify-center items-center my-5 ${experience >= 4 ? "flex" : 'hidden'} `}>
                    <h1 className={`${coupon ? 'hidden' : 'flex'}`}>Do you have a coupon</h1>
                    <input type="text" placeholder='Coupon' className={`w-[200px] p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 ${coupon ? 'flex' : 'hidden'}`} value={couponValue} name='couponValue' onChange={handleCouponChange} />
                    <button className={` bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-lg ${coupon ? 'hidden' : 'flex'}`} onClick={() => {
                        setCoupon(true)
                    }}>
                        Yes
                    </button>
                    <button className={` bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-lg ${coupon ? 'flex' : 'hidden'}`} onClick={() => {
                        handleRedeem()
                    }}>
                        {redeem ? 'Redeeming' : 'Redeem'}
                    </button>

                </div>
                {redeemMessage && (
                    <p className={` my-5 flex flex-col text-center ${redeemMessage.includes("Redemption Successful") ? "text-green-600" : "text-red-500"}`}>
                        {redeemMessage}
                    </p>
                )}
            </div>
        </div>

    )
};

