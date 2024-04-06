import streamlit as st
from datetime import datetime
import cv2
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import numpy as np
from tensorflow.keras.models import load_model
import os

# Dictionary mapping skin types to products
products_by_skin_type = {
    "Oily": [
        {"name": "Taupe Radiance routine combo", "link": "https://mytaupe.com/products/taupe-radiance-routine-combo?variant=47752711274797&currency=INR&utm_medium=product_sync&utm_source=google&utm_content=sag_organic&utm_campaign=sag_organic&gad_source=1&gclid=Cj0KCQjwwYSwBhBtEiwAFHDZx83lhhmPpOusqKuCrQNi9r59Y3DvR7y2CsL4ZQj3E1-o0aq_vgbj8hoCwSQQAvD_BwE"},
        {"name": "Cetaphil Oily Skin Cleanser", "link": "https://www.amazon.in/Cetaphil-Cleanser-Oily-Skin-125ml/dp/B01CCGW732?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A15APWRK6P7LBV"},
        {"name": "No More Oily Skin Kit", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwjPsrCluZGFAxVyzTgGHeXhAPsQvhd6BAgBEHs"},
        {"name": "Salicylic Acid For Acne-Prone Skin 100 Ml", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwjPsrCluZGFAxVyzTgGHeXhAPsQvhd6BAgBEH0"},
        {"name": "Oil Clear Clarifying Toner", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwjPsrCluZGFAxVyzTgGHeXhAPsQvhd6BAgBEI4B"},
        {"name": "Skin Dew Daily Energising Face Moisturiser Gel", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwjPsrCluZGFAxVyzTgGHeXhAPsQvhd6BAgBEJYB"}
    ],
    "Dry": [
        {"name": "Luxe Moisturizing Cream", "link": "https://www.amazon.in/Monoskin-LUXE-Moisturizing-Cream-50ml/dp/B09PHDRY9M?ref_=ast_sto_dp"},
        {"name": "CeraVe Moisturizing Cream", "link": "https://www.amazon.in/CeraVe-Moisturizing-Cream-Daily-Moisturizer/dp/B07JPYJ62Q/ref=sr_1_3?crid=1AUPRZS0UIH3U&keywords=cerave+moisturizing+cream&qid=1649382684&s=beauty&sprefix=cerave%2Cbeauty%2C350&sr=1-3"},
        {"name": "Sebamed Moisturising Cream", "link": "https://www.amazon.in/Sebamed-Moisturising-Cream-Ph-Value-5-5/dp/B07HFGTY7M/ref=sr_1_5?crid=3MZT3QCHPE93U&keywords=sebamed+moisturizing+cream&qid=1649382801&s=beauty&sprefix=sebamed+mois%2Cbeauty%2C307&sr=1-5"},
        {"name": "Forest Essentials Light Hydrating Facial Gel", "link": "https://www.amazon.in/Forest-Essentials-Hydrating-Facial-Lavender/dp/B01GZX59E8/ref=sr_1_4?crid=1MI7IR9OT7KEO&keywords=forest+essentials+facial+gel&qid=1649382854&s=beauty&sprefix=forest+ess%2Cbeauty%2C283&sr=1-4"},
        {"name": "Kama Ayurveda Eladi Hydrating Ayurvedic Face Cream", "link": "https://www.amazon.in/Kama-Ayurveda-Eladi-Hydrating-Ayurvedic/dp/B075XFGT75/ref=sr_1_3?crid=1ATVMRE2V89SS&keywords=kama+ayurveda+face+cream&qid=1649382946&s=beauty&sprefix=kama+ayurveda+fa%2Cbeauty%2C274&sr=1-3"},
        {"name": "Hydrating Face Cream", "link": "https://www.amazon.in/Avon-NutraEffects-Hydrating-Moisturiser-Normal/dp/B07TBD56WZ/ref=sr_1_6?crid=2N30V49VD79SP&keywords=hydrating+face+cream&qid=1649382993&s=beauty&sprefix=hydrating+face+%2Cbeauty%2C304&sr=1-6"}
    ],
    "acne": [
        {"name": "Snail Product Serums", "link": "https://bebodywise.com/product/snail-96-mucin-serum"},
        {"name": "Derma Oil Free", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwiU2bODu5GFAxUKyDwCHanJC8kYABADGgJzZg&ase=2&gclid=Cj0KCQjw5ImwBhBtEiwAFHDZxySYvPymc-4WZPcEi_hJlMJDpc03I1SrMAzzeUJgHdYooiu5MAM0bBoC34sQAvD_BwE&sig=AOD64_2O6RBpt1w7GluVv7n9lt8T3O-Cog&ctype=5&nis=6&adurl&ved=2ahUKEwjI8KeDu5GFAxWbl2MGHXgVAXAQvhd6BQgBEIEB"},
        {"name": "Power Assence", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwiU2bODu5GFAxUKyDwCHanJC8kYABAFGgJzZg&ase=2&gclid=Cj0KCQjw5ImwBhBtEiwAFHDZx0TUX_FHaEITtXEfII-TvB9KrytxlYi7KU0Ykou_8Fh7WmVwN_lmYBoCNfcQAvD_BwE&sig=AOD64_1CpqC6QWc2FHsYLC7GO-mvMyCvlg&ctype=5&nis=6&adurl&ved=2ahUKEwjI8KeDu5GFAxWbl2MGHXgVAXAQvhd6BQgBEIYB"},
        {"name": "Salicylic Acid", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwiU2bODu5GFAxUKyDwCHanJC8kYABAHGgJzZg&ase=2&gclid=Cj0KCQjw5ImwBhBtEiwAFHDZx9TdHLoxtxi8023vEM6r6nmKMLDZs1F3-RhXLbh6sGy0aLHn-5GqHRoCijIQAvD_BwE&sig=AOD64_0Z_vOo7dyyTmIduijdPBQkRO2v6Q&ctype=5&nis=6&adurl&ved=2ahUKEwjI8KeDu5GFAxWbl2MGHXgVAXAQvhd6BQgBEIsB"},
        {"name": "Glycolic Acid", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwiU2bODu5GFAxUKyDwCHanJC8kYABANGgJzZg&ase=2&gclid=Cj0KCQjw5ImwBhBtEiwAFHDZx0UokhyOb1EACLZzH5plqj3K3kwAb0HVO8Y21qfkkbndQio25yKJyxoCR9cQAvD_BwE&sig=AOD64_2plWZtIO18aIEeLZ_aWZ1AHmkDLw&ctype=5&nis=6&adurl&ved=2ahUKEwjI8KeDu5GFAxWbl2MGHXgVAXAQvhd6BQgBEKIB"},
        {"name": "Dermatouch", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwiU2bODu5GFAxUKyDwCHanJC8kYABAVGgJzZg&ase=2&gclid=Cj0KCQjw5ImwBhBtEiwAFHDZx8AS0fVH5FTv6bJfNXjYR4ihxmN2Q-CrBkF4hf3Vnp2pKBrgJ5c5kBoCY_wQAvD_BwE&sig=AOD64_3Nrd10M1um8eVaXmEMIhcUC0jY8Q&ctype=5&nis=6&adurl&ved=2ahUKEwjI8KeDu5GFAxWbl2MGHXgVAXAQvhd6BQgBEL4B"}
    ],
    "Normal": [
        {"name": "Advanced Snail 96 Mucin Power Essence", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABABGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZxyTImWU5mL328VSpP7RoRFwegihrKs4og8pa3KxTc0XLJNqOgCFoPhoC6G4QAvD_BwE&sig=AOD64_1Fb-hui4JxIo_5myUIG57yxet7Ww&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BAgBEHg"},
        {"name": "Ever Glow Face Wash", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABADGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx-5SnQdvwOPwP8dsk7Q4ocLee6rBLAOO72qMOkUpnoJ2Xu9pY5QyOxoCOpEQAvD_BwE&sig=AOD64_07NHzUtT9_stX9-vpgjQzsby6lDA&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BAgBEH0"},
        {"name": "Neutriderm Moisturising Lotion w/Vitamin E ", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABAFGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx9PWbmtLuQYLQTXYspkQ7NriV2ZBK9lHRnUOfTnAc_s9K2j9l18W4RoCXg0QAvD_BwE&sig=AOD64_28agN_85nKVPfBx_KTE8XgTh7fsw&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BQgBEIIB"},
        {"name": "Neutriderm Pre-Makeup Skincare", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABAHGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx8VPCNA9JACq9xS06LHEn1dR7UkhiCm3QScIJ6ZXOyUbo3jNj2-FKhoCaV8QAvD_BwE&sig=AOD64_2xPttf7bOlVOthx0KMc6_kve6uBA&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BQgBEIcB"},
        {"name": "Ceramide & Hyaluronic Face Moisturiser", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABANGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx5YhftsBYjDiGq532LdpMrOGk5_96GB8pybUFcwWx4dSsqz0rPl1SxoC7TEQAvD_BwE&sig=AOD64_1MxFpsJPVQlAU5F7wCy8m4AicaRQ&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BQgBEJ4B"},
        {"name": "Garnier Skin Naturals", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwj1iuHivJGFAxXspGYCHZMLDSoYABAPGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZxwkp4oiWaZTnrvksvAJqFXtplGaFmn41OYTCpFlk49MJM3-7AlorbhoCGn4QAvD_BwE&sig=AOD64_29OxsFuKbN1A_qj8ZqTq-C9DYiCw&ctype=5&nis=6&adurl&ved=2ahUKEwjo9NLivJGFAxXsxqACHawjDBEQvhd6BQgBEKMB"}
    ],
    "wrinkles": [
        {"name": "Anti Aging Serum with Retinol", "link": "https://ghc.health/collections/skin/products/vitamin-c-serum"},
        {"name": "Mamaearth", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABALGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx0sxT34y86XUcmDVJ4QKk1poHor8E7B92OT9E6t9i8JQ1pbs1g0X5xoCYNMQAvD_BwE&sig=AOD64_1q8Nic5jXZ40G4HShZzsgZAKbPug&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEJ4B"},
        {"name": "Neutrogena Rapid Wrinkle Repair", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABANGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZxw4RldOb-bOdA8tk9WASGJ3Cm3r4vK7Z59LQoKm2yovGbbHFGsBLGxoCf3gQAvD_BwE&sig=AOD64_38jgM8MIMtBiJxaFtEeJF4DNNQqQ&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEKMB"},
        {"name": "Dot & Key Night Reset Retinol", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAPGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx_Bgpx3bQ2KiKzjlekO6KWcZX3YL82ynyd5S7qTit99tVMfiQfm4QBoC6cMQAvD_BwE&sig=AOD64_2diefTAj5YqOYcDYbDqefxBOgjhQ&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEKgB"},
        {"name": "Retinol Regenerating Cream", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAXGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx_Jp5N6U71ubhXexJGCyKu8j9v9NN6BzzwNKZnYgarF_Npn7Z6oZrRoCkecQAvD_BwE&sig=AOD64_1J99ifdC-H3rECX18tfx0k5JlPeA&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEL4B"},
        {"name": "Anti-Ageing Night Cream", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAbGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx9zPL-pAQfgAhwFvXICP_wdwBEjG_joIsiz6_hdRWXdKzy30RcctwRoC9VIQAvD_BwE&sig=AOD64_1KK5IB-UKJga-VNpNwQi6lA7WacA&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEMwB"}
    ],
    "wrinkles": [
    {"name": "Anti Aging Serum with Retinol", "link": "https://ghc.health/collections/skin/products/vitamin-c-serum"},
    {"name": "Mamaearth", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABALGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx0sxT34y86XUcmDVJ4QKk1poHor8E7B92OT9E6t9i8JQ1pbs1g0X5xoCYNMQAvD_BwE&sig=AOD64_1q8Nic5jXZ40G4HShZzsgZAKbPug&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEJ4B"},
    {"name": "Neutrogena Rapid Wrinkle Repair", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABANGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZxw4RldOb-bOdA8tk9WASGJ3Cm3r4vK7Z59LQoKm2yovGbbHFGsBLGxoCf3gQAvD_BwE&sig=AOD64_38jgM8MIMtBiJxaFtEeJF4DNNQqQ&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEKMB"},
    {"name": "Dot & Key Night Reset Retinol", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAPGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx_Bgpx3bQ2KiKzjlekO6KWcZX3YL82ynyd5S7qTit99tVMfiQfm4QBoC6cMQAvD_BwE&sig=AOD64_2diefTAj5YqOYcDYbDqefxBOgjhQ&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEKgB"},
    {"name": "Retinol Regenerating Cream", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAXGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx_Jp5N6U71ubhXexJGCyKu8j9v9NN6BzzwNKZnYgarF_Npn7Z6oZrRoCkecQAvD_BwE&sig=AOD64_1J99ifdC-H3rECX18tfx0k5JlPeA&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEL4B"},
    {"name": "Anti-Ageing Night Cream", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi_xfjbu5GFAxVEaw8CHd53Bt4YABAbGgJ0Yg&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx9zPL-pAQfgAhwFvXICP_wdwBEjG_joIsiz6_hdRWXdKzy30RcctwRoC9VIQAvD_BwE&sig=AOD64_1KK5IB-UKJga-VNpNwQi6lA7WacA&ctype=5&nis=6&adurl&ved=2ahUKEwj75-Xbu5GFAxV77TgGHRHMA7YQvhd6BQgBEMwB"},
    {"name": "Mamaearth Bye Dark Circles Eye Cream", "link": "https://dl.flipkart.com/dl/mamaearth-bye-dark-circles-eye-cream/p/itm1009741aba0c6?pid=ECMFMUP4ZMHGKZHW&cmpid=product.share.pp&_refId=PP.0dc04a6c-aa24-4489-a936-3d70d7abd273.ECMFMUP4ZMHGKZHW&_appId=CL"},
    {"name": "Mcaffeine Coffee Hydrogel Under Eye", "link": "https://www.amazon.in/Mcaffeine-Puffiness-Reduction-Hyaluronic-Moisture-Lock/dp/B0BJF757CK?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A2A53F3N8CEFWW"},
    {"name": "5% Caffeine Under Eye Serum", "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi6tru3upGFAxU5o2YCHVeJBfIYABAHGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx5fvMM9FMWA9463dyQmtryT8FJIJDP0ARoeUJiFtDsAlAQPOPG341RoCX8cQAvD_BwE&sig=AOD64_1LQfZH3rJ71sb9_zlqjiPvASxdLQ&ctype=5&nis=6&adurl&ved=2ahUKEwitnq-3upGFAxVVrWMGHRBnB98Qvhd6BAgBEG8"},
    ],
    "darkcircles": [
    {
      "name": "mamaearth",
      "link": "https://dl.flipkart.com/dl/mamaearth-bye-dark-circles-eye-cream/p/itm1009741aba0c6?pid=ECMFMUP4ZMHGKZHW&cmpid=product.share.pp&_refId=PP.0dc04a6c-aa24-4489-a936-3d70d7abd273.ECMFMUP4ZMHGKZHW&_appId=CL"
    },
    {
      "name": "Mcaffeine Coffee Hydrogel Under Eye",
      "link": "https://www.amazon.in/Mcaffeine-Puffiness-Reduction-Hyaluronic-Moisture-Lock/dp/B0BJF757CK?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A2A53F3N8CEFWW"
    },
    {
      "name": "5% Caffeine Under Eye Serum",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi6tru3upGFAxU5o2YCHVeJBfIYABAHGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx5fvMM9FMWA9463dyQmtryT8FJIJDP0ARoeUJiFtDsAlAQPOPG341RoCX8cQAvD_BwE&sig=AOD64_1LQfZH3rJ71sb9_zlqjiPvASxdLQ&ctype=5&nis=6&adurl&ved=2ahUKEwitnq-3upGFAxVVrWMGHRBnB98Qvhd6BAgBEG8"
    },
    {
      "name": "EYE Am Enough- Under Eye",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi6tru3upGFAxU5o2YCHVeJBfIYABAJGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZxxbWvbYibXga2BMrEGrVRY9zWOl6pa6x4N-GviOy3MDzytj32jHB4xoCG5sQAvD_BwE&sig=AOD64_2ZBNe4vTpKyTurkrkWtNsra6-fFg&ctype=5&nis=6&adurl&ved=2ahUKEwitnq-3upGFAxVVrWMGHRBnB98Qvhd6BAgBEHg"
    },
    {
      "name": "Under Eye Cream for Dark Circles Removal & Wrinkles",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi6tru3upGFAxU5o2YCHVeJBfIYABALGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx3vDV4mIfYiZwAyppbwHHzmb3a7J3NLknv0GRzvxk0LZUO-NRc8nthoCdYkQAvD_BwE&sig=AOD64_395ZSfqwK7CLdB6dkLhnIT9CrKnQ&ctype=5&nis=6&adurl&ved=2ahUKEwitnq-3upGFAxVVrWMGHRBnB98Qvhd6BAgBEH0"
    },
    {
      "name": "L’Oréal Paris Glycolic Bright Dark Circle Eye Serum with 3%",
      "link": "https://www.google.com/aclk?sa=l&ai=DChcSEwi6tru3upGFAxU5o2YCHVeJBfIYABAPGgJzbQ&ase=2&gclid=CjwKCAjw5ImwBhBtEiwAFHDZx_U8LAAGThhHcAV-f70FzrLk30_BCk4DDUn3lbzqn9TztuTqnLeeRxoCQkoQAvD_BwE&sig=AOD64_0B9-OCKlfshgp1kb2jhMcMj_Mvfw&ctype=5&nis=6&adurl&ved=2ahUKEwitnq-3upGFAxVVrWMGHRBnB98Qvhd6BQgBEIcB"
    }
  ]
}

st.title('Skin Type Cosmetic Recommendation System')
run = st.checkbox('Run Camera')

FRAME_WINDOW = st.image([])
camera = cv2.VideoCapture(0)

while run:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    FRAME_WINDOW.image(frame)

    cv2.imwrite('./uploads/test.jpg', frame)
    run = False
    break

model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

def model_predict(img_path, model, class_names):
    # Load and preprocess the image
    image = Image.open(img_path).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    # Make prediction
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    
    return class_name[2:-1], confidence_score

# Get skin type prediction
skin_type, confidence = model_predict('./uploads/test.jpg', model, class_names)

# Display the skin type prediction and confidence score
st.write(f"Detected Skin Type: {skin_type}")
print(len(skin_type))
st.write(f"Confidence Score: {confidence}")

# Display products based on the detected skin type

st.write("Detected Skin Type:", skin_type)  # Debugging statement

if skin_type in products_by_skin_type:
    st.write("Recommended Products:")
    for product in products_by_skin_type[skin_type]:
        st.write(f"Name: {product['name']}")
        st.write(f"Link: {product['link']}")
else:
    st.write("No products available for this skin type.")

# Close the webcam
camera.release()