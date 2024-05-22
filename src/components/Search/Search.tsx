import React, {
  use,
  useEffect,
  useState,
  CSSProperties,
  useMemo,
  useCallback,
} from "react";
import axios, { AxiosError } from "axios";
import Link from "next/link";
import Image from "next/image";
import { CSVLink } from "react-csv";
import logo from "../../../public/company logo.png";
import { ClipLoader } from "react-spinners";
import ReactSelect, { MultiValue, Options, createFilter } from "react-select";
import {
  ErrorMessage,
  FormikConsumer,
  FormikContext,
  FormikProvider,
  useFormik,
} from "formik";
import * as Yup from "yup";

const override: CSSProperties = {
  display: "block",
  margin: "0 auto",
  borderColor: "red",
};

const LIMIT = 1000 as const;

interface SearchResult {
  city: string;
  results: {
    title: string;
    snippet: string;
    link: string;
    images: { src: string }[];
  }[];
  search_content: string;
}
type FormValues = {
  countries: MultiValue<DropDownOptions>;
  locations: MultiValue<DropDownOptions>;
  searchContent: string;
  numResults: number;
  email: string;
};
type DropDownOptions = {
  value: string;
  label: string;
};
const SearchByLocationSchema = Yup.object({
  countries: Yup.array(
    Yup.object({ value: Yup.string(), label: Yup.string() })
  ).min(1, "Please select any country"),
  locations: Yup.array(
    Yup.object({ value: Yup.string(), label: Yup.string() })
  ).min(1, "Please select any location"),
  searchContent: Yup.string().required("Please enter any search keyword"),
  numResults: Yup.number()
    .min(1, "Please select number of results more than 0")
    .required("Please enter number of results"),
  email: Yup.string()
    .email("Please enter valid email")
    .required("Please enter your email"),
});
export const Search = () => {
  const [allCountries, setAllCountries] = useState<DropDownOptions[]>([]);
  const [allLocaions, setAllLocations] = useState<DropDownOptions[]>([]);
  const [search, setSearch] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const [experience, setExperience] = useState(0);
  const [coupon, setCoupon] = useState(false);
  const [couponValue, setCouponValue] = useState("");
  const [redeem, setRedeem] = useState(false);
  const [verify, setVerify] = useState(false);
  const [redeemMessage, setRedeemMessage] = useState("");
  const [csvresults, setCsvResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>("");
  const formik = useFormik<FormValues>({
    initialValues: {
      locations: [],
      countries: [],
      searchContent: "",
      numResults: 0,
      email: "",
    },
    validationSchema: SearchByLocationSchema,
    onSubmit: verifyUser,
  });
  const {
    values,
    setFieldValue,
    handleChange,
    handleBlur,
    handleSubmit,
    handleReset,
  } = formik;
  const handleCouponChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCouponValue(e.target.value);
  };

  const fetchCountries = async () => {
    try {
      const response = await axios.get(
        "https://geopositioning.uxlivinglab.online/api/get-countries"
      );
      if (response?.data && response?.data?.countries) {
        let tempCountries = response?.data.countries?.map((item: string) => ({
          label: item,
          value: item,
        }));
        setAllCountries(tempCountries);
      }
    } catch (error) {
      console.error("Error fetching countries:", error);
    }
  };

  const fetchLocation = () => {
    try {
      const body = {
        selectedCountries: values.countries.map((item) => item.label),
        offset: 0,
        limit: 17000,
      };
      axios
        .post(
          "https://geopositioning.uxlivinglab.online/api/get-locations",
          body
        )
        .then((response) => {
          if (response.status === 200) {
            const responseData = Object.values(response.data).flatMap(
              (item: any) => item?.data
            );
            const tempLocations: DropDownOptions[] = [];
            responseData.forEach((item: any) => {
              if (item?.name) {
                tempLocations.push({ value: item.name, label: item.name });
              }
            });
            setAllLocations(tempLocations);
          }
        });
    } catch (error) {
      console.error("Error fetching locations:", error);
    }
  };

  const handleSearch = async () => {
    try {
      setVerify(false);
      setSearch(true);
      const body = {
        location: values.locations.map((item) => item.value),
        search: values.searchContent,
        num_results: values.numResults,
        email: values.email,
        occurrences: experience,
      };
      const response = await axios.post(
        "https://geopositioning.uxlivinglab.online/api/",
        body
      );
      if (response.status === 200) {
        const newSearchResults = response.data?.search_results;

        setResults(newSearchResults as SearchResult[]);
        const mergedResults = Object.values(newSearchResults).reduce(
          (prev: any, curr: any) =>
            prev.concat(
              curr?.results?.map((item: any) => ({
                ...item,
                city: curr?.city ?? "",
                images: item?.images
                  ?.map((image: any) => image?.src ?? "")
                  ?.join(","),
              }))
            ),
          []
        );
        setCsvResults(mergedResults as any[]);
        setFieldValue("locations", []);
        setFieldValue("countries", []);
        setSearch(false);
      } else {
        setSearch(false);
      }
    } catch (error) {
      console.error("Error fetching search results:", error);
      setSearch(false);
    }
  };

  const handleRedeem = async () => {
    try {
      const response = await axios.post(
        "https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=redeem_coupon",
        {
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: values.email,
            coupon: couponValue,
            product_number: "UXLIVINGLAB004",
          }),
        }
      );

      if (response.status === 200) {
        setRedeemMessage("Redemption successful!"); // Set success message
        setRedeem(false); // Hide coupon input
        setCoupon(true); // Hide coupon input
        setCouponValue(""); // Clear coupon input
      } else {
        setRedeemMessage(response.data.message || "Redemption failed"); // Set failure message
        setCouponValue(""); // Clear coupon input
      }
      setTimeout(() => {
        setRedeemMessage("");
      }, 5000);
    } catch (error) {
      console.error("Error while redeeming:", error);
      setRedeemMessage("Error while redeeming. Please try again.");
      setCouponValue(""); // Clear coupon input

      setTimeout(() => {
        setRedeemMessage("");
      }, 5000);
    }
  };

  async function verifyUser(values: FormValues) {
    try {
      if (errorMessage) {
        setErrorMessage("");
      }

      setVerify(true);
      setIsLoading(true);
      const body = {
        product_number: "UXLIVINGLAB004",
        email: values.email,
      };

      const response = await axios.post(
        "https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=register_user",
        body
      );

      if (response.data.success) {
        const response = await axios.get(
          `https://100105.pythonanywhere.com/api/v3/experience_database_services/?type=get_user_email&product_number=UXLIVINGLAB004&email=${values.email}`
        );

        if (response.data.success) {
          const occurence = response.data?.occurrences;
          setExperience(occurence);
          setIsLoading(false);
        } else {
          setIsLoading(false);
          setErrorMessage(response?.data?.message);
        }
      } else {
        setIsLoading(false);
        setErrorMessage(response?.data?.message);
      }
    } catch (error: any | AxiosError) {
      setErrorMessage(
        error?.response?.data?.message
          ? error?.response?.data?.message
          : "Failed to serve your request"
      );
      setIsLoading(false);
    }
  }

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    fetchLocation();
  }, [values.countries]);

  return (
    <div className="w-full h-full flex flex-col md:flex-row bg-white ">
      <div
        className={`p-5 space-y-5 flex flex-col justify-center items-center md:flex-row md:space-x-20 ${
          verify ? "opacity-30" : ""
        } `}
      >
        <div className="w-full h-full xl:flex-row lg:flex-row md:flex-col-reverse sm:flex-col-reverse  flex justify-start space-y-5  items-center">
          <div className="w-full flex p-5  space-y-5 flex-col">
            <div className="flex flex-col w-full justify-center md:h-[120px] p-2 items-center">
              <div className="w-[100px] h-[100px]">
                <Image src={logo} alt="" className="w-full h-full" />
              </div>
              <h1 className="text-[1.5rem] font-medium">
                Location Specific Search
              </h1>
            </div>
            <FormikProvider value={formik}>
              <form onSubmit={handleSubmit} className="space-y-3">
                <div className="space-y-1">
                  <label htmlFor="">Select Country(s)</label>
                  <ReactSelect
                    options={allCountries}
                    value={values.countries}
                    isMulti={true}
                    id="countries"
                    name="countries"
                    onChange={(value) => setFieldValue("countries", value)}
                    onBlur={handleBlur}
                    placeholder="Select country"
                  />
                  <ErrorMessage name="countries" />
                </div>
                <div className="space-y-1 -z-10">
                  <label htmlFor="">Select Location(s)</label>
                  <ReactSelect
                    filterOption={createFilter({
                      ignoreAccents: false,
                    })}
                    options={allLocaions}
                    value={values.locations}
                    isMulti={true}
                    id="locations"
                    name="locations"
                    onChange={(value) => setFieldValue("locations", value)}
                    placeholder="Select locations"
                  />
                  <ErrorMessage name="locations" />
                </div>
                <div className="space-y-1">
                  <label htmlFor="searchContent">Search Keyword</label>
                  <input
                    type="text"
                    placeholder="Hotel, Restaurant, Park..."
                    className="w-full p-2 border-[1px] border-gray-300 rounded-md focus:outline-none focus:border-2 focus:border-blue-500"
                    name="searchContent"
                    id="searchContent"
                    value={values.searchContent}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <ErrorMessage name="searchContent" />
                </div>

                <div className="space-y-1">
                  <label htmlFor="numResults">Number of Results</label>
                  <input
                    type="number"
                    placeholder="Number of results "
                    className="w-full p-2 border-[1px] border-gray-300 rounded-md focus:outline-none focus:border-2 focus:border-blue-500"
                    name="numResults"
                    id="numResults"
                    value={values.numResults}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <ErrorMessage name="numResults" />
                </div>
                <div className="space-y-1">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="w-full p-2 border-[1px] border-gray-300 rounded-md focus:outline-none focus:border-2 focus:border-blue-500"
                    name="email"
                    id="email"
                    value={values.email}
                    onChange={handleChange}
                    onBlur={handleBlur}
                  />
                  <ErrorMessage name="email" />
                </div>
                <div className="flex space-x-5 w-full">
                  <button
                    type="submit"
                    className={`w-[40%] bg-[#61b84c] hover:bg-[#62b84cda] text-white text-[12px] font-bold py-4 px-6 rounded-full focus:outline-none focus:ring focus:border-green-500 ${
                      search ? "cursor-not-allowed opacity-60" : ""
                    }`}
                  >
                    {search ? "Searching..." : "Search"}
                  </button>
                  <button
                    type="reset"
                    className="w-[30%] p-2 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-full focus:outline-none text-[12px] focus:ring focus:border-red-500 "
                    onClick={handleReset}
                  >
                    Reset
                  </button>
                </div>
              </form>
            </FormikProvider>
            <div className="space-y-2">
              <h2 className="text-xl font-normal">Location Specific Search</h2>
              <p className="text-sm font-light">
                DoWell UX Living Lab will search in the web by positioning our
                server to the selected locations.
              </p>
              <h2 className="text-xl font-normal">How it works</h2>
              <p className="text-sm font-light">
                DoWell UX Living Lab will position the web server using the
                latitude and longitude of each location specified by the user
                and execute a search based on keywords.
              </p>
              <h2 className="text-xl font-normal">How to use</h2>
              <p className="text-sm font-light">
                Search Scenario - I am selling Yogurt, I want to analyze search
                results in different locations for my product.
              </p>
              <p className="text-sm font-medium">Disclaimer:</p>
              <p className="text-sm font-light">
                We do not assume responsibility for the accuracy of the results.
                Variations from search engine results may occur. Use information
                at your own discretion.
              </p>

              <a href="https://visitorbadge.io/status?path=https%3A%2F%2Fgeopositioning.uxlivinglab.online%2Fapi%2F">
                <img
                  src="https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fgeopositioning.uxlivinglab.online%2Fapi%2F&countColor=%23263759"
                  className="mt-5"
                />
              </a>
            </div>
          </div>
          <div className="w-full h-full flex flex-col  justify-start items-center">
            <div className="flex flex-wrap max-w-full rounded-t-lg justify-between items-center md:max-w-full gap-2 md:min-w-[60px] max-h-[250px] min-h-[100px] pb-3 mb-10">
              {results?.length ? (
                results.map((data, index) => (
                  <button
                    onClick={() => setActiveIndex(index)}
                    className={`${
                      activeIndex === index
                        ? "bg-[#3B82F6] text-white"
                        : "bg-gray-400 text-black"
                    } hover:bg-[#3B82F6] hover:text-white transition-all w-[30%] rounded-t-lg  min-h-[70px] max-h-[80px] max-w-full flex justify-center text-center px-3 py-2 items-center grow `}
                    key={index}
                  >
                    <span>{`${data.results.length} search results for "${data.search_content}" in  ${data.city}`}</span>
                  </button>
                ))
              ) : (
                <></>
              )}
            </div>

            {results?.length ? (
              <div className="bg-white w-full bottom-0  p-5 max-w-full max-h-[850px] overflow-y-auto ">
                {results
                  ?.find((_, index) => index === activeIndex)
                  ?.results?.map((result, index) => (
                    <div
                      className="flex flex-col w-full  border-b-2 p-3 space-y-4 "
                      key={index}
                    >
                      <Link
                        href={result.link}
                        className="md:text-[25px] text-[20px] text-blue-600 hover:text-red-500"
                        target="_blank"
                      >
                        {result.title}
                      </Link>
                      <p className="md:text-[18px] text-[14px]">
                        {result.snippet}
                      </p>
                      <div className="md:w-[400px] h-[200px] sm:w-svw max-h-[200px] flex justify-start border-2">
                        {result.images.length ? (
                          <Image
                            src={`${result.images[0].src}`}
                            width={400}
                            height={400}
                            alt=""
                            className="sm:w-full object-cover object-center"
                          />
                        ) : null}
                      </div>
                    </div>
                  ))}

                <button
                  className={`p-3 hover:text-green-500 text-[20px] font-bold `}
                >
                  <CSVLink data={csvresults}>
                    Click to download search results
                  </CSVLink>
                </button>
              </div>
            ) : (
              <div className="max-w-full max-h-full overflow-y-auto flex flex-col justify-center items-center">
                <p className="text-5xl font-thin">No Results</p>
                <p className="text-sm font-thin">Fill details to get results</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div
        className={`fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 shadow-sm w-[90%] md:w-[500px] min-h-[350px] max-h-[450px] bg-white rounded-md ${
          verify ? "flex" : "hidden"
        } justify-start items-center flex-col`}
      >
        <div
          onClick={() => {
            setVerify(false);
          }}
          className="w-[20px] h-[20px] top-5 p-1 right-5 text-gray-400 font-normal rounded-md hover:text-white bg-transparent hover:bg-red-600 flex items-center absolute justify-center"
        >
          X
        </div>
        <div className="flex w-full flex-col-reverse justify-between  p-2  items-center">
          <h1 className="text-[1.2rem] font-bold">Location specific Search</h1>
          <div className="w-[100px] h-[100px]">
            <Image src={logo} alt="" className="w-full h-full" />
          </div>
        </div>

        <div className="flex  justify-center items-center text-cener">
          {isLoading ? (
            <div className="ml-3 flex justify-center items-center">
              <ClipLoader color="black" loading={isLoading} size={17} />
              <h1>Loading</h1>
            </div>
          ) : errorMessage ? (
            <h1 className="w-full flex justify-center items-center text-center">
              {errorMessage}
            </h1>
          ) : (
            <h1 className="w-full flex justify-center items-center text-center">
              You have used Location Specific Search {experience} times
            </h1>
          )}{" "}
        </div>
        <div className="flex w-[80%] justify-center gap-2 items-center my-10">
          <button
            className="bg-gray-400 py-2 px-4 hover:bg-red-600 text-white font-bold rounded-full"
            onClick={() => {
              setVerify(false);
            }}
          >
            Cancel
          </button>
          <button
            className={`bg-[#61b84c] hover:bg-[#62b84cda] py-2 px-4 text-white font-bold rounded-full ${
              experience >= 6 ? "hidden" : "flex"
            } ${isLoading ? "cursor-not-allowed" : "cursor-pointer"}`}
            disabled={isLoading || experience >= 6}
            onClick={handleSearch}
          >
            Continue
          </button>
          <button
            className={`${
              experience >= 4 ? "flex" : "hidden"
            } bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-full`}
          >
            <Link
              href="https://dowellpay.online/contribute-payment/?product_number=UXLIVINGLAB004"
              target="_blank"
            >
              Contribute
            </Link>
          </button>
        </div>

        <div
          className={`flex space-x-4 justify-center items-center my-5 ${
            experience >= 4 ? "flex" : "hidden"
          } `}
        >
          <h1 className={`${coupon ? "hidden" : "flex"}`}>
            Do you have a coupon
          </h1>
          <input
            type="text"
            placeholder="Coupon"
            className={`w-[200px] p-2 border-2 border-gray-300 rounded-md focus:outline-none focus:border-blue-500 ${
              coupon ? "flex" : "hidden"
            }`}
            value={couponValue}
            name="couponValue"
            onChange={handleCouponChange}
          />
          <button
            className={` bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-lg ${
              coupon ? "hidden" : "flex"
            }`}
            onClick={() => {
              setCoupon(true);
            }}
          >
            Yes
          </button>
          <button
            className={` bg-green-600 py-2 px-4 hover:bg-gray-400 text-white font-bold rounded-lg ${
              coupon ? "flex" : "hidden"
            }`}
            onClick={() => {
              handleRedeem();
            }}
          >
            {redeem ? "Redeeming" : "Redeem"}
          </button>
        </div>
        {redeemMessage && (
          <p
            className={` my-5 flex flex-col text-center ${
              redeemMessage.includes("Redemption Successful")
                ? "text-green-600"
                : "text-red-500"
            }`}
          >
            {redeemMessage}
          </p>
        )}
      </div>
    </div>
  );
};