from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import pandas as pd
import io

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Lead Scoring Bot running"}

@app.post("/score")
async def score_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    df["score"] = 0

    if "rating" in df.columns:
        df.loc[df["rating"] >= 4.5, "score"] += 25

    if "reviews" in df.columns:
        df.loc[df["reviews"] >= 100, "score"] += 30
        df.loc[(df["reviews"] >= 50) & (df["reviews"] < 100), "score"] += 20

    if "website" in df.columns:
        df.loc[df["website"].notna(), "score"] += 15

    if "phone" in df.columns:
        df.loc[df["phone"].notna(), "score"] += 10

    if "city" in df.columns:
        df.loc[df["city"].isin(["Madrid", "Barcelona", "Valencia"]), "score"] += 20

    df = df.sort_values(by="score", ascending=False)

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scored_leads.csv"}
    )
